#!/usr/bin/env python
"""
A script coupling data from MPDS with AiiDA
"""

from mpds_client import MPDSDataRetrieval
from aiida_crystal.aiida_compatibility import dbenv


def mpds():
    """Using mpds_client library"""
    client = MPDSDataRetrieval(api_key='mNNpIcYMGgSF9LXbwfieyYSlQ7DMdPTuac4DrfRn4pgFv7PO')

    answer = client.get_data(
        {"elements": "K", "classes": "binary", "props": "atomic structure"},
        fields={'S': [
            'phase_id',
            'entry',
            'chemical_formula',
            'cell_abc',
            'sg_n',
            'setting',
            'basis_noneq',
            'els_noneq'
        ]}
    )
    return answer


@dbenv
def main():
    """A function retrieving data from MPDS"""
    from aiida.tools.dbimporters import DbImporterFactory
    importer = DbImporterFactory('mpds')(api_key='mNNpIcYMGgSF9LXbwfieyYSlQ7DMdPTuac4DrfRn4pgFv7PO')
    results = importer.query({"elements": "K",
                              "classes": "binary",
                              "props": "atomic structure"})
    # returns an iterator of Cif entries


def example():
    """With direct access to API"""
    from urllib.parse import urlencode
    import httplib2
    import json

    api_key = "mNNpIcYMGgSF9LXbwfieyYSlQ7DMdPTuac4DrfRn4pgFv7PO"
    endpoint = "https://api.mpds.io/v0/download/facet"
    search = {
        "elements": "K",
        "classes": "binary, oxide",
        "props": "isothermal bulk modulus",  # see https://mpds.io/#hierarchy
        "lattices": "cubic"
    }

    req = httplib2.Http()
    response, content = req.request(
        uri=endpoint + '?' + urlencode({
            'q': json.dumps(search),
            'pagesize': 10,
            'dtype': 2  # see query string parameters documentation
        }),
        method='GET',
        headers={'Key': api_key}
    )

    if response.status != 200:
        # NB 400 means wrong input, 403 means authorization issue etc.
        # see https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
        raise RuntimeError("Error code %s" % response.status)

    content = json.loads(content)

    if content.get('error'):
        raise RuntimeError(content['error'])

    print("OK, got %s hits" % len(content['out']))


if __name__ == "__main__":
    print(mpds())
