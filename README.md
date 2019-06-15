Service for pairing requests and invoices

### Installation:
There is no need to compile anything. Running
```
docker-compose up --build
```
should end with spawned postgresql database pre-populated with some testing
data and admin user.

Administration interface is accessible at `http://localhost:8000/admin`. Use
dev admin account `admin/admin`.


### Configuration:

Use `campaign_reports/settings.py` settings for production or
`campaign_reports/settings_local.py` for development. Most important setting
is `PDF_ANALYZER_URL` which should point to running instance of [FB invoice
analyzer](https://github.com/cvt-oss/fb-invoice-pdf-analyzer).

### API:
`http://localhost:8000/v1/` gives you a browsable API for getting requests
and reports.

First you'll want to feed database with some data from parsed invoices. It
has to be trigerred by e.g.

```
http http://127.0.0.1:8000/v1/invoice invoice_id=123
```

It expects, that PDF analyzer already parsed the PDF and data can be retrieved
from there and return this response:

```json
HTTP/1.1 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Length: 26
Content-Type: application/json
Date: Sat, 15 Jun 2019 13:35:05 GMT
Server: WSGIServer/0.2 CPython/3.7.3
Vary: Accept, Cookie
X-Frame-Options: SAMEORIGIN

{
    "analyzer_invoice_id": 1,
    "invoice_id": 5,
    "items": 2
}
```

If invoice already exists, it is overwritten by new data.

Now you can query reports for merged data from requests and invoices.


```
http  http://127.0.0.1:8000/v1/invoice/5/
```

```json
HTTP/1.1 200 OK
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
Content-Length: 282
Content-Type: application/json
Date: Sat, 15 Jun 2019 13:37:39 GMT
Server: WSGIServer/0.2 CPython/3.7.3
Vary: Accept, Cookie
X-Frame-Options: SAMEORIGIN

{
    "campaigns": [
        {
            "requests": [
                {
                    "id": 3,
                    "approved": true
                }
            ],
            "name": "CampaignName1",
            "price": 1001.86
        },
        {
            "request": [
                {
                    "id": 3,
                    "similarity": 0.608696
                }
            ],
            "name": "CampaignName2",
            "price": 201.97
        }
    ],
    "dt_payment": "2019-01-19T15:56:00Z",
    "id": 5,
    "total": 101.0,
    "transaction_id": "sampleTransactionId"
}
```

For each campaing you can get following variants:

 1) It contains only one item with 'accepted' field. It means, that it was
 reviewed and it is 100% match of request and campaign.

 2) It contains 0-10 items ordere by 'similarity' field. It is textual
 similarity to diffrent requests and has to be reviewed by human.

Note, that you can filter list of all invoices based on dates. So, if you
want to see invoices issued in 2019, run

```
http  'http://127.0.0.1:8000/v1/invoice/?min_date=2019-01-01&max_date=2020-01-01'
```
