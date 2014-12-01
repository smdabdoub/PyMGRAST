"""
This module represents a Python interface to the MG-RAST API.
Specifically, this module contains methods that directly call exposed methods
provided by the API. Value-added methods are elsewhere.
"""
import requests
import json

class MGRASTException(Exception):
    """
    A representation of a generic error returned by the MG-RAST API.
    """
    pass

class MGRASTAuthenticationException(MGRASTException):
    """
    An MGRASTException specifically representing a failed authentication 
    attempt.
    """
    pass

def mgrast_request(method, item_id=None, params=None, auth_key=None, debug=False):
    """
    Makes an MG-RAST API call
    """
    auth = {'auth': auth_key} if auth_key else {}
    item_id = '' if item_id is None else '/'+item_id
    join_mult = lambda item: '&'.join(['{}={}'.format(item[0],entry) for entry in item[1]])
    params = '?' + '&'.join(['='.join(item) if not isinstance(item[1],list) else join_mult(item) for item in params.items()]) if params else ''
    url = 'http://api.metagenomics.anl.gov/1/{method}{ID}{params}'
    fURL = url.format(method=method, ID=item_id, params=params)

    if debug:
        print fURL
        return

    # submit request
    resp = requests.get(fURL, headers=auth)

    if resp.headers['content-type'] == 'application/json':
        text = json.loads(resp.text)
        if 'ERROR' in text:
            if ('insufficient permissions' in text['ERROR'] or
                'authentication failed' in text['ERROR']):
                raise MGRASTAuthenticationException(text['ERROR'])
            raise MGRASTException(text['ERROR'])

    return resp

def id_check(prefix, ID):
    """
    Checks that an identifier such as a project or metagenome ID has the
    appropriate prefix required by MG-RAST when sending API queries.
    For example, project IDs begin with 'mgp' - 'mgp1111'.
    """
    if not ID.startswith(prefix):
        ID = prefix + ID
    return ID

def project_metagenomes(project_id, match=None, auth_key=None):
    """
    Given an MG-RAST project ID, download a list of all metagenome IDs belonging
    to that project.
    """
    project_id = id_check('mgp', project_id)
    if match is None:
        match = ['']

    r = mgrast_request('project', project_id, {'verbosity':'full'}, auth_key)
    project_data = json.loads(r.text)

    metagenomes = {}

    for mg_id in [mg[0] for mg in project_data['metagenomes']]:
        r = mgrast_request('metagenome', mg_id, {'verbosity': 'minimal'}, auth_key)
        mg_info = json.loads(r.text)
        # find maximally matching name
        for m in sorted(match, key=lambda x: len(x), reverse=True):
            if m in mg_info['name']:
                metagenomes[mg_id] = mg_info['name']

    return metagenomes


def sequence_annotation(mg_id, database, dtype, auth_key, **params):
    """
    Retrieve annotated sequence data for a single metagenome against a database.
    Takes an MG-RAST metagenome ID, an m5nr source database (KEGG, SEED, ...),
    and a data type (function, organism, ontology, feature).

    The returned tabular data is in the format:
    sequence id, m5nr id (md5sum), dna sequence, semicolon separated list of
    annotations

    :@return: A list of result rows split into lists containing the above 
              tabular data.
    """
    mg_id = id_check('mgm', mg_id)
    if params is None:
        params = {}
    params.update({'source': database, 'type': dtype})
    r = mgrast_request('annotation/sequence', mg_id, params, auth_key=auth_key)
    if r.text.rfind('Download complete') == 0:
        raise Exception('Data download incomplete')
    return [x.split('\t') for x in r.text.split('\n')[1:-2]]


def similarity_annotation(mg_id, database, dtype, auth_key, **params):
    """
    Retrieve annotated similarity data for a single metagenome against a
    database.
    Takes an MG-RAST metagenome ID, an m5nr source database (KEGG, SEED, ...),
    and a data type (function, organism, ontology, feature).

    The returned tabular data is in the format:
    sequence id, m5nr id (md5sum), list of similarity-related scores

    :@return: A list of result rows split into lists containing the above
              tabular data.
    """
    mg_id = id_check('mgm', mg_id)
    if params is None:
        params = {}
    params.update({'source': database, 'type': dtype})
    r = mgrast_request('annotation/similarity', mg_id, params, auth_key=auth_key)
    if r.text.rfind('Download complete') == 0:
        raise Exception('Data download incomplete')
    return [x.split('\t') for x in r.text.split('\n')[1:-2]]


def download_metagenome_data(metagenomes, func, database='KEGG', dtype='function', params=None, auth_key=None):
    """
    Apply an MG-RAST API 'download' function to a list of metagenome IDs and return the data
    as a list of results for each given metagenome.
    """
    results = []
    params = {} if params is None else params
    for mg in metagenomes:
        results.extend(func(mg, database, dtype, auth_key))
    return results
