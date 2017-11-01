#Python Client Examples

```
from perch-client import PerchAPIClient

perch = PerchAPIClient(username='username@example.com', password='your-perch-password', api_key='your-api-key')

perch.me.get()

perch.indicators.create(
    company_id=1,
    communities=[5, 10],
    title='Test Indicator',
    description='Description for test indicator',
    tlp=2,
    confidence=3,
    operator=1,
    observables=[{'type': 2, 'details': 'this is one bad hombre.']
)

```