import cerberus
import semantic_version


def validate_semver(field, value, error):
    try:
        semantic_version.Version.parse(value)
    except ValueError as e:
        error(field, f"{e}")


def validate_semver_range(field, value, error):
    try:
        semantic_version.Spec.parse(value)
    except ValueError as e:
        error(field, f'{e}')


schema = {
    'name': {'type': 'string', 'required': True},
    'target': {'type': 'string', 'allowed': ['v5', 'cortex']},
    'location': {'type': 'string'},
    'metadata': {
        'type': 'dict',
        'schema': {
            'description': {'type': 'string'},
            'website': {'type': 'string'},
            'license': {'type': 'string'},
            'authors': {'type': 'list', 'schema': {'type': 'string'}},
            'keywords': {'type': 'list', 'schema': {'type': 'string'}}
        }
    },
    'versions': {
        'type': 'dict',
        'required': True,
        'keysrules': {'type': 'string', 'check_with': validate_semver},
        'valuesrules': {
            'oneof': [
                # shorthand rule
                {'type': 'string', 'check_with': validate_semver_range},
                # full rule
                {
                    'type': 'dict',
                    'empty': False,
                    'schema': {
                        'kernel': {'type': 'string', 'check_with': validate_semver_range},
                        'location': {'type': 'string'},
                        'target': {'type': 'string', 'allowed': ['v5', 'cortex']}
                    }
                }
            ]
        }
    }
}


def validate(validator, data):
    cerberus_verdict = validator.validate(data)

    # make sure that either top level location template is specified or all versions have location specified
    custom_verdict = data.get('location') is not None or all(
        [version.get('location', None) is not None for version in data.get('versions') if isinstance(version, dict)]
    )

    if custom_verdict:
        location_errors = validator.errors.get('location', [])
        location_errors.append('location must be specified once at the top level or in all versions')
        validator.errors['location'] = location_errors

    return cerberus_verdict and custom_verdict
