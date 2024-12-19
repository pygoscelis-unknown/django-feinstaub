import requests


def get(url) -> requests.Response:
    try:
        page = requests.get(url, timeout=None)
        page.raise_for_status()
        return page
    except requests.exceptions.HTTPError as eh:
        raise requests.exceptions.HTTPError(eh)
    except requests.exceptions.Timeout as et:
        raise requests.exceptions.Timeout(et)
    except requests.exceptions.ConnectionError as ec:
        raise requests.exceptions.ConnectionError(ec)
    except requests.exceptions.RequestException as ex:
        raise requests.exceptions.RequestException(ex)
