"""
# Copyright  (c) 2011-2016, Hortonworks Inc.  All rights reserved.
#
# Except as expressly permitted in a written agreement between your
# company and Hortonworks, Inc, any use, reproduction, modification,
# redistribution, sharing, lending or other exploitation of all or
# any part of the contents of this file is strictly prohibited.
#
"""

from random import choice
from string import ascii_letters as letters

import logging
import pytest

from beaver_common.version_utils import Version
from beaver.component.atlas_resources.atlasv2 import AtlasV2
from tests.atlas.utils.searchUtils import SearchUtils as searchUtils
from tests.atlas.split3.faceted_search.data.input_data import InputData as input_data
from tests.atlas.utils.quickSearchUtils import QuickSearchUtils as quick_search_utils

pytestmark = [
    pytest.mark.canary_Search,
    pytest.mark.skipif(
        Version.current() < "7.1.6",
        reason="Test suite only supported for 7.1.6+ (CDPQE-2645)",
    ),
]

logger = logging.getLogger(__name__)
type_names = [
    "hive_table",
    "hbase_namespace",
    "impala_process",
    "kafka_topic",
    "ml_project",
]
all_type_names = ["_ALL_ENTITY_TYPES", "hive_table"]
service_types = ["hive", "hbase", "impala", "kafka", "ml"]
invalid_types = ["lorem", "ipsum", "hello", "world"]
test_types = ["hive_table"]
# Uncomment once CDPD-22537 is fixed, aggregationMetrics is missing in
# quick_search GET/POST API when "typeName": "_ALL_ENTITY_TYPES"
# test_types = ["_ALL_ENTITY_TYPES", "hive_table"]


classification_sys_attr = "__classificationNames"
propagated_classification_sys_attr = "__propagatedClassificationNames"


@pytest.mark.L0
@pytest.mark.ci_precommit_group2
@pytest.mark.custom_kerberos_principal
@pytest.mark.parametrize("_type", test_types)
def test_single_classification(_type):
    """
    Associate a classification to an entity
    Fire search with single classification and verify results
    :param _type:
    :return:
    """
    tag = "tag_%s" % ("".join(choice(letters) for i in range(5))).lower()
    AtlasV2.create_tag(tag_name=tag, attrib_map=input_data.attrib_map)
    table = "table_%s" % ("".join(choice(letters) for i in range(5))).lower()
    table_guid = searchUtils.create_table_get_guid(table_name=table)
    AtlasV2.associate_traits_to_entity(trait_name=tag, entity_guid=table_guid)
    entity_filters_list = [(classification_sys_attr, "eq", tag)]
    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        expected_entities_guids=[table_guid],
    )
    # disassociate tag and verify
    AtlasV2.dis_associate_traits(trait_name=tag, entity_guid=table_guid)
    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        expected_entities_guids=[],
    )


@pytest.mark.parametrize("_type", test_types)
def test_unknown_classification(_type):
    """'
    Verify search with unknown classification returns no results
    """
    tag = "tag_%s" % ("".join(choice(letters) for i in range(5))).lower()
    entity_filters_list = [(classification_sys_attr, "eq", tag)]

    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        expected_entities_guids=[],
    )


@pytest.mark.parametrize("_type", test_types)
def test_one_classification_among_multiple(_type):
    """'
    Associate multiple tags to an entity
    Fire search with 1 tag and verify results
    """
    pattern = ("".join(choice(letters) for i in range(5))).lower()
    for i in range(0, 3):
        AtlasV2.create_tag(
            tag_name="tag_%s_%s" % (pattern, i), attrib_map=input_data.attrib_map
        )
    table = "table_%s" % ("".join(choice(letters) for i in range(5))).lower()
    table_guid = searchUtils.create_table_get_guid(table_name=table)
    for i in range(0, 3):
        AtlasV2.associate_traits_to_entity(
            trait_name="tag_%s_%s" % (pattern, i), entity_guid=table_guid
        )
    entity_filters_list = [(classification_sys_attr, "eq", "tag_%s_%s" % (pattern, 1))]
    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        expected_entities_guids=[table_guid],
    )


@pytest.mark.parametrize("_type", test_types)
@pytest.mark.parametrize("condition", ["AND", "OR"])
def test_all_classifications_with_condition(_type, condition):
    """
    Fire search with all associated classifications with OR and AND conditions
    """
    pattern = ("".join(choice(letters) for i in range(5))).lower()
    for i in range(0, 3):
        AtlasV2.create_tag(
            tag_name="tag_%s_%s" % (pattern, i), attrib_map=input_data.attrib_map
        )
    table = "table_%s" % ("".join(choice(letters) for i in range(5))).lower()
    table_guid = searchUtils.create_table_get_guid(table_name=table)
    for i in range(0, 3):
        AtlasV2.associate_traits_to_entity(
            trait_name="tag_%s_%s" % (pattern, i), entity_guid=table_guid
        )
    entity_filters_list = [
        (classification_sys_attr, "eq", "tag_%s_%s" % (pattern, 0)),
        (classification_sys_attr, "eq", "tag_%s_%s" % (pattern, 1)),
        (classification_sys_attr, "eq", "tag_%s_%s" % (pattern, 2)),
    ]

    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        expected_entities_guids=[table_guid],
    )


@pytest.mark.parametrize("_type", test_types)
def test_not_equals_classification(_type):
    """
    Fire search with eq , neq classification names
    """
    tag = "tag_%s" % ("".join(choice(letters) for i in range(5))).lower()
    AtlasV2.create_tag(tag_name=tag, attrib_map=input_data.attrib_map)
    table = "table_%s" % ("".join(choice(letters) for i in range(5))).lower()
    table_guid = searchUtils.create_table_get_guid(table_name=table)
    AtlasV2.associate_traits_to_entity(trait_name=tag, entity_guid=table_guid)
    entity_filters_list = [(classification_sys_attr, "eq", tag)]

    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        expected_entities_guids=[table_guid],
    )
    # disassociate tag and verify
    AtlasV2.dis_associate_traits(trait_name=tag, entity_guid=table_guid)
    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        expected_entities_guids=[],
    )


@pytest.mark.parametrize("_type", test_types)
def test_null_classifications(_type):
    """
    Fire search with isNull condition
    :param _type:
    :return:
    """
    entity_filters_list = quick_search_utils.construct_attribute_filter(
        [
            (classification_sys_attr, "isNull", ""),
            (propagated_classification_sys_attr, "isNull", ""),
        ]
    )
    response, response_status = AtlasV2.post_quick_search(
        type_name=_type, entity_filters_list=entity_filters_list
    )
    assert response_status == 200
    for entity in response["searchResults"]["entities"]:
        assert not entity["classificationNames"]


@pytest.mark.parametrize("_type", test_types)
def test_not_null_classifications(_type):
    """
    Fire search with notNull condition
    :param _type:
    :return:
    """
    entity_filters_list = quick_search_utils.construct_attribute_filter(
        [(classification_sys_attr, "notNull", "")]
    )
    response, response_status = AtlasV2.post_quick_search(
        type_name=_type, entity_filters_list=entity_filters_list
    )
    assert response_status == 200
    for entity in response["searchResults"]["entities"]:
        assert entity["classificationNames"]


@pytest.mark.xfail(True, reason="CDPD-7850")
@pytest.mark.parametrize("_type", test_types)
def test_search_with_parent_tag(_type):
    """
    Fire search with parent tag and verify entities associated to its child tag are returned
    :param _type:
    :return:
    """
    ptag = "ptag_%s" % ("".join(choice(letters) for i in range(5))).lower()
    AtlasV2.create_tag(tag_name=ptag, attrib_map=input_data.attrib_map)
    ctag = "ctag_%s" % ("".join(choice(letters) for i in range(5))).lower()
    AtlasV2.create_tag(tag_name=ctag, parent_tag=ptag)

    table = "table_%s" % ("".join(choice(letters) for i in range(5))).lower()
    table_guid = searchUtils.create_table_get_guid(table_name=table)
    AtlasV2.associate_traits_to_entity(trait_name=ctag, entity_guid=table_guid)
    entity_filters_list = [(classification_sys_attr, "eq", ptag)]
    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        expected_entities_guids=[table_guid],
    )


@pytest.mark.parametrize("_type", test_types)
def test_search_with_same_system_and_basic_search_attribute(_type):
    """
    Fire search with basic search param "classification" and system attr "__classificationNames" with same tag
    """
    tag = "tag_%s" % ("".join(choice(letters) for i in range(5))).lower()
    AtlasV2.create_tag(tag_name=tag, attrib_map=input_data.attrib_map)
    table = "table_%s" % ("".join(choice(letters) for i in range(5))).lower()
    table_guid = searchUtils.create_table_get_guid(table_name=table)
    AtlasV2.associate_traits_to_entity(
        trait_name=tag, entity_guid=table_guid, attrib_map=input_data.tag_attrib_data[0]
    )
    entity_filters_list = [(classification_sys_attr, "eq", tag)]
    tag_filters_list = [("string", "eq", "str1")]

    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        classification=tag,
        tag_filters_list=quick_search_utils.construct_attribute_filter(
            tag_filters_list
        ),
        expected_entities_guids=[table_guid],
    )


@pytest.mark.parametrize("_type", test_types)
def test_search_with_different_system_and_basic_search_attribute(_type):
    """
    Fire search with basic search param "classification" and system attr "__classificationNames" with different tag
    """
    btag = "tag_%s" % ("".join(choice(letters) for i in range(5))).lower()
    stag = "tag_%s" % ("".join(choice(letters) for i in range(5))).lower()
    AtlasV2.create_tag(tag_name=btag, attrib_map=input_data.attrib_map)
    AtlasV2.create_tag(tag_name=stag, attrib_map=input_data.attrib_map)
    table = "table_%s" % ("".join(choice(letters) for i in range(5))).lower()
    table_guid = searchUtils.create_table_get_guid(table_name=table)
    AtlasV2.associate_traits_to_entity(
        trait_name=btag,
        entity_guid=table_guid,
        attrib_map=input_data.tag_attrib_data[0],
    )
    AtlasV2.associate_traits_to_entity(
        trait_name=stag,
        entity_guid=table_guid,
        attrib_map=input_data.tag_attrib_data[0],
    )
    entity_filters_list = [(classification_sys_attr, "eq", stag)]
    tag_filters_list = [("string", "eq", "str1")]

    quick_search_utils.quick_search_post_util_compare_by_guids(
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        tag_filters_list=quick_search_utils.construct_attribute_filter(
            tag_filters_list
        ),
        classification=btag,
        expected_entities_guids=[table_guid],
    )


@pytest.mark.parametrize("_type", test_types)
def test_with_query(_type):
    """
    Fire  "__classificationNames" search with query param
    :param _type:
    :return:
    """
    tag = "tag_%s" % ("".join(choice(letters) for i in range(5))).lower()
    AtlasV2.create_tag(tag_name=tag, attrib_map=input_data.attrib_map)
    table = "table_%s" % ("".join(choice(letters) for i in range(5))).lower()
    table_guid = searchUtils.create_table_get_guid(table_name=table)
    AtlasV2.associate_traits_to_entity(
        trait_name=tag, entity_guid=table_guid, attrib_map=input_data.tag_attrib_data[0]
    )
    entity_filters_list = [(classification_sys_attr, "eq", tag)]
    quick_search_utils.quick_search_post_util_compare_by_guids(
        query=table,
        type_name=_type,
        entity_filters_list=quick_search_utils.construct_attribute_filter(
            entity_filters_list
        ),
        classification=tag,
        expected_entities_guids=[table_guid],
    )
