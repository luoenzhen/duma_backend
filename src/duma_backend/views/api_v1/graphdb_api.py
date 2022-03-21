import logging
import os

import requests
from flask import Response, abort, current_app, jsonify, redirect, request
from flask_tern import openapi
from flask_tern.auth import current_user, require_user
from tern_rdf.sparql import process_sparql_result, sparql

from .blueprint import bp


def replace_value(resource, orginal_str, item, obj):
    """replace query variable value"""
    str_to_be_replaced = resource + "_" + item
    if obj and item in obj:
        orginal_str = orginal_str.replace(str_to_be_replaced, obj[item])
    return orginal_str


# Note: source of truth for platform is in a spreadsheet in google drive;
# Note: source of truth for unit is QUDT, if it's not in there, user need to submit
# the new unit to QUDT and if accepted, TERN airflow will pull the new QUDT unit into graphdb;
# Note: parameter and parameters are duplicated, the reason is because it used to be plural
# for legacy record it still uses plural;
def get_query_dict(resource, label="", uri="", record_obj=None):
    """query dict"""

    knowledge_graph_url = (
        current_app.config["SPARQL_URL"]
        + current_app.config["SPARQL_REPOSITORY"]
        + current_app.config["SPARQL_REPOSITORY_KNOWLEDGE_GRAPH_CORE"]
    )
    vocab_graph_url = (
        current_app.config["SPARQL_URL"]
        + current_app.config["SPARQL_REPOSITORY"]
        + current_app.config["SPARQL_REPOSITORY_VOCAB_CORE"]
    )
    qudt_graph_url = (
        current_app.config["SPARQL_URL"]
        + current_app.config["SPARQL_REPOSITORY"]
        + current_app.config["SPARQL_REPOSITORY_QUDT"]
    )

    query_dict = {
        "person": {
            "query_endpoint": knowledge_graph_url,
            "post_endpoint": knowledge_graph_url + "/statements",
            "query": """
                PREFIX schema: <http://schema.org/>
                select * from <https://w3id.org/tern/resources/>
                where {
                    ?uri a schema:Person .
                    optional { ?uri schema:name ?name }
                    filter(str(?name) in ("${label}"))
                }
            """,
            "post_query": """
                PREFIX schema: <http://schema.org/>
                PREFIX tern-org: <https://w3id.org/tern/ontologies/org/>
                INSERT DATA
                {
                    GRAPH <https://w3id.org/tern/resources/> {
                        <${uri}> a schema:Person .
                        <${uri}> schema:name "${label}" .
                        <${uri}> schema:givenName "person_given_name" .
                        <${uri}> schema:familyName "person_surname" .
                        <${uri}> schema:email "person_email" .
                        <${uri}> tern-org:orcID "person_orcid" .
                    }
                }
            """,
        },
        "organization": {
            "query_endpoint": knowledge_graph_url,
            "post_endpoint": knowledge_graph_url + "/statements",
            "query": """
                PREFIX schema: <http://schema.org/>
                select * from <https://w3id.org/tern/resources/>
                where {
                    ?uri a schema:Organization .
                    optional { ?uri schema:name ?name }
                    filter(str(?name) in ("${label}"))
                }
            """,
            "post_query": """
                PREFIX schema: <http://schema.org/>
                INSERT DATA
                {
                    GRAPH <https://w3id.org/tern/resources/> {
                        <${uri}> a schema:Organization .
                        <${uri}> schema:name "${label}" .
                        <${uri}> schema:email "organization_email" .
                    }
                }
            """,
        },
        "instrument": {
            "query_endpoint": knowledge_graph_url,
            "post_endpoint": knowledge_graph_url + "/statements",
            "query": """
                PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                select * where {
                    ?uri a tern:Instrument .
                    optional { ?uri rdfs:label ?label }
                    filter(str(?label) in ("${label}"))
                }
            """,
            "post_query": """
                PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX schema: <http://schema.org/>
                INSERT DATA
                {
                    GRAPH <https://w3id.org/tern/resources/> {
                        <${uri}> a tern:Instrument .
                        <${uri}> rdfs:label "${label}" .
                        <${uri}> schema:serialNumber "instrument_serial" .
                    }
                }
            """,
        },
        "parameter": {
            "query_endpoint": vocab_graph_url,
            "post_endpoint": vocab_graph_url + "/statements",
            "query": """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                select * where {
                    ?uri a skos:Concept ;
                    skos:inScheme <http://linked.data.gov.au/def/tern-cv/5699eca7-9ef0-47a6-bcfb-9306e0e2b85e> .
                    optional { ?uri skos:prefLabel ?label }
                    filter(str(?label) in ("${label}"))
                }
                """,
            "post_query": """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX dcterms: <http://purl.org/dc/terms/>
                INSERT DATA
                {
                    GRAPH <http://linked.data.gov.au/def/tern-cv/> {
                        <${uri}> a skos:Concept .
                        <${uri}> skos:prefLabel "${label}" .
                        <${uri}> skos:definition "parameter_description" .
                        <${uri}> dcterms:source "parameter_source" .
                        <${uri}> skos:inScheme <http://linked.data.gov.au/def/tern-cv/5699eca7-9ef0-47a6-bcfb-9306e0e2b85e> .
                    }
                }
            """,
        },
        "platform": {
            "query_endpoint": knowledge_graph_url,
            "post_endpoint": knowledge_graph_url + "/statements",
            "query": """
                PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                select * where {
                    ?uri a tern:Platform .
                    optional { ?uri rdfs:label ?label }
                    filter(str(?label) in ("${label}"))
                }
                """,
            "post_query": """
                PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                INSERT DATA
                {
                    GRAPH <https://w3id.org/tern/resources/> {
                        <${uri}> a tern:Platform .
                        <${uri}> rdfs:label "${label}" .
                    }
                }
            """,
        },
        "unit": {
            "query_endpoint": qudt_graph_url,
            "post_endpoint": qudt_graph_url + "/statements",
            "query": """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX qudt: <http://qudt.org/schema/qudt/>
                select * where {
                    ?uri a qudt:Unit ;
                    optional { ?uri rdfs:label ?label }
                    filter(str(?label) in ("${label}"))
                }
                """,
            "post_query": """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX qudt: <http://qudt.org/schema/qudt/>
                INSERT DATA
                {
                    GRAPH <http://qudt.org/vocab/unit/> {
                        <${uri}> a qudt:Unit .
                        <${uri}> rdfs:label "${label}" .
                    }
                }
            """,
        },
        "organization_site": {
            "query_endpoint": knowledge_graph_url,
            "post_endpoint": knowledge_graph_url + "/statements",
            "query": """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX org: <http://www.w3.org/ns/org#>
                select * where {
                    ?uri a org:Site ;
                    optional { ?uri rdfs:label ?label }
                    filter(str(?label) in ("${label}"))
                }
                """,
            "post_query": """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX org: <http://www.w3.org/ns/org#>
                INSERT DATA
                {
                    GRAPH <https://w3id.org/tern/resources/> {
                        <${uri}> a org:Site .
                        <${uri}> rdfs:label "organization_site_full_address_line" .
                        <${uri}> org:siteOf "organization_site_uri_organization" .
                        <${uri}> org:siteAddress "organization_site_uri_postal_address" .
                    }
                }
            """,
        },
        "postal_address": {
            "query_endpoint": knowledge_graph_url,
            "post_endpoint": knowledge_graph_url + "/statements",
            "query": """
                PREFIX schema: <http://schema.org/>
                PREFIX tern-org: <https://w3id.org/tern/ontologies/org/>
                select * where {
                    ?uri a schema:PostalAddress ;
                    optional { ?uri tern-org:fullAddressLine ?label }
                    filter(str(?label) in ("${label}"))
                }
                """,
            "post_query": """
                PREFIX schema: <http://schema.org/>
                PREFIX tern-org: <https://w3id.org/tern/ontologies/org/>
                INSERT DATA
                {
                    GRAPH <https://w3id.org/tern/resources/> {
                        <${uri}> a schema:PostalAddress .
                        <${uri}> tern-org:fullAddressLine "postal_address_full_address_line" .
                        <${uri}> schema:streetAddress "postal_address_street_address" .
                        <${uri}> schema:addressLocality "postal_address_address_locality" .
                        <${uri}> schema:addressRegion "postal_address_address_region" .
                        <${uri}> schema:addressCountry "postal_address_country" .
                        <${uri}> schema:postalCode "postal_address_postcode" .
                    }
                }
            """,
        },
    }
    query_dict[resource]["query"] = query_dict[resource]["query"].replace("${label}", label)
    query_dict[resource]["post_query"] = (
        query_dict[resource]["post_query"].replace("${label}", label).replace("${uri}", uri)
    )

    if resource == "person":
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "given_name", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "surname", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "email", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "orcid", record_obj
        )

    if resource == "organization":
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "email", record_obj
        )

    if resource == "instrument":
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "serial", record_obj
        )

    if resource == "parameter":
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "description", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "source", record_obj
        )

    if resource == "postal_address":
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "full_address_line", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "street_address", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "address_locality", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "address_region", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "country", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "postcode", record_obj
        )

    if resource == "organization_site":
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "full_address_line", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "uri_organization", record_obj
        )
        query_dict[resource]["post_query"] = replace_value(
            resource, query_dict[resource]["post_query"], "uri_postal_address", record_obj
        )

    return query_dict


def get_result(resource, label):
    """get result from graphdb"""
    logger = logging.getLogger(__name__)
    logger.info("\tCalling get_result resource: %s\n, label: %s\n", resource, label)

    query_dict = get_query_dict(resource, label)
    endpoint = query_dict[resource]["query_endpoint"]
    logger.info("\tendpoint: %s\n", endpoint)
    query = query_dict[resource]["query"]
    logger.info("\tquery: %s\n", query)
    query_result = sparql(endpoint, query)
    query_result = process_sparql_result(query_result, key_value_not_a_list=["label"])
    logger.info("\tget_result query_result is %s\n", query_result)
    return query_result


# get records from GraphDB
@bp.route("/graphdb/search/<resource>/<label>", methods=["GET"])
@require_user
@openapi.validate()
def graphdb_get(resource, label):
    """get query result from graphdb"""
    logger = logging.getLogger(__name__)
    logger.info("\tCalling graphdb_get\n")
    query_result = get_result(resource, label)
    result = {}
    for k, v in query_result.items():
        result["data"] = v

    return jsonify(result)


# post record to GraphDB
@bp.route("/graphdb/post/<resource>", methods=["POST"])
@require_user
@openapi.validate()
def graphdb_post(resource):
    """post records to graphdb"""
    logger = logging.getLogger(__name__)
    logger.info("\tCalling graphdb_post()\n")

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/sparql-results+json",
    }

    record_obj = request.get_json()
    logger.info("\trequest body is %s\n", record_obj)

    if resource == "organization":
        label = record_obj["name"]
    elif resource == "person":
        label = record_obj["canonical_name"]
    else:
        label = record_obj["label"]

    # print("record_obj", record_obj)
    if record_obj["userAddedCategory"] == "organization":
        # check if existing postal_address in graphdb
        # insert data to postal_address, then organization
        # finally insert data to organization_site
        existing_postal_address = get_result("postal_address", record_obj["full_address_line"])
        logger.info("\texisting_postal_address: %s\n", existing_postal_address)

        if not existing_postal_address:
            postal_address_uri = record_obj["uri_postal_address"]
            postal_address_post_dict = get_query_dict("postal_address", uri=postal_address_uri, record_obj=record_obj)
            postal_address_post_endpoint = postal_address_post_dict["postal_address"]["post_endpoint"]
            logger.info("\tendpoint for postal address: %s\n", postal_address_post_endpoint)
            postal_address_post_query = postal_address_post_dict["postal_address"]["post_query"]
            logger.info("\tpost_query for postal address: %s\n", postal_address_post_query)
            result_postal_address = requests.post(
                postal_address_post_endpoint,
                auth=(current_app.config["SPARQL_USER"], current_app.config["SPARQL_PASS"]),
                headers=headers,
                data=f"update={postal_address_post_query}",
            )
            logger.info("\tresult_postal_address: %s\n", result_postal_address)

            # add organization to graphdb
            organization_uri = record_obj["uri"]
            organization_post_dict = get_query_dict("organization", label, organization_uri, record_obj)
            organization_endpoint = organization_post_dict["organization"]["post_endpoint"]
            logger.info("\tendpoint for organization: %s\n", organization_endpoint)
            organization_post_query = organization_post_dict["organization"]["post_query"]
            logger.info("\tpost_query for organization: %s\n", organization_post_query)
            result_organization = requests.post(
                organization_endpoint,
                auth=(current_app.config["SPARQL_USER"], current_app.config["SPARQL_PASS"]),
                headers=headers,
                data=f"update={organization_post_query}",
            )
            logger.info("\tresult_organization: %s\n", result_organization)

            # add organization site to graphdb with above site uri and organization uri
            organization_site_uri = record_obj["uri_organization_site"]
            organization_site_post_dict = get_query_dict("organization_site", label, organization_site_uri, record_obj)
            organization_site_endpoint = organization_site_post_dict["organization_site"]["post_endpoint"]
            logger.info("\tendpoint for organization site: %s\n", organization_site_endpoint)
            organization_site__post_query = organization_site_post_dict["organization_site"]["post_query"]
            logger.info("\tpost_query for organization site: %s\n", organization_site__post_query)
            result_organization_site = requests.post(
                organization_site_endpoint,
                auth=(current_app.config["SPARQL_USER"], current_app.config["SPARQL_PASS"]),
                headers=headers,
                data=f"update={organization_site__post_query}",
            )
            logger.info("\tresult_organization_site: %s\n", result_organization_site)
        # else when get existing postal address
        else:
            existing_postal_address_uri = list(existing_postal_address.keys())[0]
            logger.info("\texisting_postal_address_uri: %s\n", existing_postal_address_uri)
            record_obj["uri_postal_address"] = existing_postal_address_uri
            # add organization to graphdb
            organization_uri = record_obj["uri"]
            organization_post_dict = get_query_dict("organization", label, organization_uri, record_obj)
            organization_endpoint = organization_post_dict["organization"]["post_endpoint"]
            logger.info("\tendpoint for organization: %s\n", organization_endpoint)
            organization_post_query = organization_post_dict["organization"]["post_query"]
            record_obj["uri_organization"] = organization_uri
            logger.info("\tpost_query for organization: %s\n", organization_post_query)
            result_organization = requests.post(
                organization_endpoint,
                auth=(current_app.config["SPARQL_USER"], current_app.config["SPARQL_PASS"]),
                headers=headers,
                data=f"update={organization_post_query}",
            )
            logger.info("\tresult_organization: %s\n", result_organization)

            # add the postal_address_uri and organization uri to a new organzation site
            organization_site_uri = record_obj["uri_organization_site"]
            organization_site_post_dict = get_query_dict("organization_site", label, organization_site_uri, record_obj)
            organization_site_endpoint = organization_site_post_dict["organization_site"]["post_endpoint"]
            logger.info("\tendpoint for organization site: %s\n", organization_site_endpoint)
            organization_site__post_query = organization_site_post_dict["organization_site"]["post_query"]
            logger.info("\tpost_query for organization site: %s\n", organization_site__post_query)
            result_organization_site = requests.post(
                organization_site_endpoint,
                auth=(current_app.config["SPARQL_USER"], current_app.config["SPARQL_PASS"]),
                headers=headers,
                data=f"update={organization_site__post_query}",
            )
            logger.info("\tresult_organization_site: %s\n", result_organization_site)
        result = {"data": result_organization.status_code}
        return jsonify(result)
    else:
        uri = record_obj["uri"]
        post_dict = get_query_dict(resource, label, uri, record_obj)
        endpoint = post_dict[resource]["post_endpoint"]
        logger.info("\tendpoint: %s\n", endpoint)
        post_query = post_dict[resource]["post_query"]
        logger.info("\tpost_query: %s\n", post_query)

        result = {}
        result = requests.post(
            endpoint,
            auth=(current_app.config["SPARQL_USER"], current_app.config["SPARQL_PASS"]),
            headers=headers,
            data=f"update={post_query}",
        )
        logger.info("\tresult is: %s\n", result.status_code)
        result = {"data": result.status_code}
        return jsonify(result)
