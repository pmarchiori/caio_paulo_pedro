# ZAP Scanning Report

ZAP by [Checkmarx](https://checkmarx.com/).


## Summary of Alerts

| Risk Level | Number of Alerts |
| --- | --- |
| High | 0 |
| Medium | 0 |
| Low | 1 |
| Informational | 2 |




## Insights

| Level | Reason | Site | Description | Statistic |
| --- | --- | --- | --- | --- |
| Low | Warning |  | ZAP warnings logged - see the zap.log file for details | 3    |
| Info | Informational | http://127.0.0.1:8000 | Percentage of responses with status code 2xx | 55 % |
| Info | Informational | http://127.0.0.1:8000 | Percentage of responses with status code 4xx | 44 % |
| Info | Informational | http://127.0.0.1:8000 | Percentage of endpoints with content type application/json | 42 % |
| Info | Informational | http://127.0.0.1:8000 | Percentage of endpoints with content type text/css | 14 % |
| Info | Informational | http://127.0.0.1:8000 | Percentage of endpoints with content type text/html | 14 % |
| Info | Informational | http://127.0.0.1:8000 | Percentage of endpoints with content type text/javascript | 28 % |
| Info | Informational | http://127.0.0.1:8000 | Percentage of endpoints with method GET | 100 % |
| Info | Informational | http://127.0.0.1:8000 | Count of total endpoints | 7    |







## Alerts

| Name | Risk Level | Number of Instances |
| --- | --- | --- |
| Timestamp Disclosure - Unix | Low | Systemic |
| Modern Web Application | Informational | 1 |
| Non-Storable Content | Informational | Systemic |




## Alert Detail



### [ Timestamp Disclosure - Unix ](https://www.zaproxy.org/docs/alerts/10096/)



##### Low (Low)

### Description

A timestamp was disclosed by the application/web server. - Unix

* URL: http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js
  * Node Name: `http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `1518500249`
  * Other Info: `1518500249, which evaluates to: 2018-02-13 05:37:29.`
* URL: http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js
  * Node Name: `http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `1732584193`
  * Other Info: `1732584193, which evaluates to: 2024-11-26 01:23:13.`
* URL: http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js
  * Node Name: `http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `1750603025`
  * Other Info: `1750603025, which evaluates to: 2025-06-22 14:37:05.`
* URL: http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js
  * Node Name: `http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `1859775393`
  * Other Info: `1859775393, which evaluates to: 2028-12-07 04:16:33.`
* URL: http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js
  * Node Name: `http://127.0.0.1:8000/static/swagger/swagger-ui-bundle.js`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `1894007588`
  * Other Info: `1894007588, which evaluates to: 2030-01-07 09:13:08.`

Instances: Systemic


### Solution

Manually confirm that the timestamp data is not sensitive, and that the data cannot be aggregated to disclose exploitable patterns.

### Reference


* [ https://cwe.mitre.org/data/definitions/200.html ](https://cwe.mitre.org/data/definitions/200.html)


#### CWE Id: [ 497 ](https://cwe.mitre.org/data/definitions/497.html)


#### WASC Id: 13

#### Source ID: 3

### [ Modern Web Application ](https://www.zaproxy.org/docs/alerts/10109/)



##### Informational (Medium)

### Description

The application appears to be a modern web application. If you need to explore it automatically then the Client Spider may well be more effective than the standard one.

* URL: http://127.0.0.1:8000/docs
  * Node Name: `http://127.0.0.1:8000/docs`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `<script src='/static/swagger/swagger-ui-bundle.js'></script>`
  * Other Info: `No links have been found while there are scripts, which is an indication that this is a modern web application.`


Instances: 1

### Solution

This is an informational alert and so no changes are required.

### Reference




#### Source ID: 3

### [ Non-Storable Content ](https://www.zaproxy.org/docs/alerts/10049/)



##### Informational (Medium)

### Description

The response contents are not storable by caching components such as proxy servers. If the response does not contain sensitive, personal or user-specific information, it may benefit from being stored and cached, to improve performance.

* URL: http://127.0.0.1:8000/
  * Node Name: `http://127.0.0.1:8000/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: http://127.0.0.1:8000/robots.txt
  * Node Name: `http://127.0.0.1:8000/robots.txt`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: http://127.0.0.1:8000/sitemap.xml
  * Node Name: `http://127.0.0.1:8000/sitemap.xml`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: http://127.0.0.1:8000/static/swagger/init.js
  * Node Name: `http://127.0.0.1:8000/static/swagger/init.js`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``

Instances: Systemic


### Solution

The content may be marked as storable by ensuring that the following conditions are satisfied:
The request method must be understood by the cache and defined as being cacheable ("GET", "HEAD", and "POST" are currently defined as cacheable)
The response status code must be understood by the cache (one of the 1XX, 2XX, 3XX, 4XX, or 5XX response classes are generally understood)
The "no-store" cache directive must not appear in the request or response header fields
For caching by "shared" caches such as "proxy" caches, the "private" response directive must not appear in the response
For caching by "shared" caches such as "proxy" caches, the "Authorization" header field must not appear in the request, unless the response explicitly allows it (using one of the "must-revalidate", "public", or "s-maxage" Cache-Control response directives)
In addition to the conditions above, at least one of the following conditions must also be satisfied by the response:
It must contain an "Expires" header field
It must contain a "max-age" response directive
For "shared" caches such as "proxy" caches, it must contain a "s-maxage" response directive
It must contain a "Cache Control Extension" that allows it to be cached
It must have a status code that is defined as cacheable by default (200, 203, 204, 206, 300, 301, 404, 405, 410, 414, 501).

### Reference


* [ https://datatracker.ietf.org/doc/html/rfc7234 ](https://datatracker.ietf.org/doc/html/rfc7234)
* [ https://datatracker.ietf.org/doc/html/rfc7231 ](https://datatracker.ietf.org/doc/html/rfc7231)
* [ https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html ](https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html)


#### CWE Id: [ 524 ](https://cwe.mitre.org/data/definitions/524.html)


#### WASC Id: 13

#### Source ID: 3


