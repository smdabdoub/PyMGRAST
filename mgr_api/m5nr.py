"""
This module implements API calls for the 'm5nr' set of functions. 
This includes: ontology, taxonomy, sources, accession, alias, md5, function,
organism, and sequence.

See http://api.metagenomics.anl.gov//api.html#m5nr for full details and
descriptions.
"""
import json
from mgr_api import api


def ontology_annotations(database='KO', **kwargs):
    """
    Download a functional hierarchy for the specified database in m5nr.
    """
    if kwargs is None:
        kwargs = {}
    kwargs.update({'source': database})
    req = api.mgrast_request('m5nr/ontology', '', params=kwargs)
    return {entry['accession']: entry for entry in json.loads(req.text)['data']}
    
def md5(checksum_id, **kwargs):
    """
    Return annotation or sequence information for the specified M5NR ID.
    The full set of optional parameters for this API call is available through
    keyword arguments (kwargs).
    
    Example response: http://api.metagenomics.anl.gov/m5nr/md5/000821a2e2f63df1a3873e4b280002a8?source=InterPro
    
    :type checksum_id: string
    :param checksum_id: The M5NR ID (in the form of an md5 checksum)
    :type kwargs: dict
    :param kwargs: Support for all optional arguments to the API call: format,
                   limit, offset, order, sequence, source, and version
    :rtype: dict
    :return: JSON-encoded results in a dictionary with one or more data entries:
             accession (string), alias (list of strings), function (string),
             md5 (string), ncbi_tax_id (int), organism (string), 
             source (string), type (string). Additionally, the following 
             entries: limit, next, offset, prev, total_count, url, and version.
    """
    if kwargs is None:
        kwargs = {}
        
    req = api.mgrast_request('m5nr/md5', checksum_id, params=kwargs)
    return json.loads(req.text)