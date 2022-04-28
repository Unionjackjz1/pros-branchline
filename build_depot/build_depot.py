import argparse
import cerberus
import jsonpickle
import pathlib
import yaml

from pros.conductor.templates.template import BaseTemplate

from .schema import schema, validate
schema_validator = cerberus.Validator(schema)


def main():
    parser = argparse.ArgumentParser('build a pros remote depot file from some yaml files')
    parser.add_argument('name')
    parser.add_argument('dirs', metavar='dir', type=pathlib.Path, nargs='+')
    args = parser.parse_args()

    directory: pathlib.Path
    for directory in args.dirs:
        if not directory.is_dir():
            print(f'{directory} is not a directory, skipping')
        else:
            template_objects = []
            templates = {
                f'{template.stem}': yaml.safe_load(template.open('r'))
                for template in directory.iterdir() if template.suffix == '.yaml'
            }
            failure = False
            for name, data in templates.items():
                print(f'Validating {name}.yaml: ', end='')
                verdict = validate(schema_validator, data)
                print(f'{"PASS" if verdict else "FAIL"}')

                if not verdict:
                    print(f'Errors:\n{yaml.dump(schema_validator.errors)}')
                    failure = True
                else:
                    for version, val in data.get('versions').items():
                        location = val.get('location', data.get('location')) \
                            if isinstance(val, dict) else data.get('location')
                        target = val.get('target', data.get('target')) if isinstance(val, dict) else data.get('target')

                        template_objects.append(BaseTemplate(
                            metadata=dict(
                                {'location': location.format(name=data.get('name'), version=version)},
                                **data.get('metadata', {})
                            ),
                            name=data.get('name'),
                            supported_kernels=val.get('kernel') if isinstance(val, dict) else val,
                            target=target,
                            version=version
                        ))

            if not failure:
                print(f'Writing depot {args.name}.json')
                with open(f'{args.name}.json', 'w') as depot:
                    depot.write(jsonpickle.pickler.encode(template_objects, indent=3))

                return 0

            return -1

