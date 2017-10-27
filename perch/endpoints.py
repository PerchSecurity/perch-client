# Ideally, endpoints will be discoverable some how in the future.
# Query variables are supported. Name your variable with whatever kwarg you want to replace it.
# For example: /users/:id

ENDPOINTS = [
    {
        'name': 'me',
        'path': '/me',
        'verbs': ('GET',)
    },
    {
        'name': 'indicators',
        'path': '/company/:company_id/indicators',
        'verbs': ('POST',)
    }
]
