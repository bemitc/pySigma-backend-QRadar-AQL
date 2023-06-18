import pytest
from sigma.collection import SigmaCollection

from sigma.backends.QRadarAQL import QRadarAQLBackend


@pytest.fixture
def QRadar_backend():
    return QRadarAQLBackend()


def test_QRadar_and_expression(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                sel:
                    fieldA: valueA
                    fieldB: valueB
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE fieldA='valueA' AND fieldB='valueB'"
           ]


def test_QRadar_or_expression(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                sel1:
                    fieldA: valueA
                sel2:
                    fieldB: valueB
                condition: 1 of sel*
        """)
    ) == [
               "SELECT * FROM events WHERE fieldA='valueA' OR fieldB='valueB'"
           ]


def test_QRadar_and_or_expression(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                sel:
                    fieldA:
                        - valueA1
                        - valueA2
                    fieldB:
                        - valueB1
                        - valueB2
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE (fieldA IN('valueA1', 'valueA2'))"
               " AND (fieldB IN('valueB1', 'valueB2'))"
           ]


def test_QRadar_or_and_expression(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                sel1:
                    fieldA: valueA1
                    fieldB: valueB1
                sel2:
                    fieldA: valueA2
                    fieldB: valueB2
                condition: 1 of sel*
        """)
    ) == [
               "SELECT * FROM events WHERE fieldA='valueA1' AND fieldB='valueB1'"
               " OR fieldA='valueA2' AND fieldB='valueB2'"
           ]


def test_QRadar_in_expression(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                sel:
                    fieldA:
                        - valueA
                        - valueB
                        - valueC*
                condition: sel
        """)
    ) == [
        "SELECT * FROM events WHERE fieldA='valueA' OR fieldA='valueB' OR LOWER("
        "fieldA) LIKE 'valuec%'"
               # "SELECT * FROM events WHERE fieldA IN('valueA', 'valueB', 'valueC%')"
           ]


def test_QRadar_regex_query(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                sel:
                    fieldA|re: foo.*bar
                    fieldB: foo
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE fieldA MATCHES 'foo.*bar' AND fieldB='foo'"
           ]


def test_QRadar_cidr_query(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                sel:
                    field|cidr: 192.168.0.0/16
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE INCIDR('192.168.0.0/16', field)"
           ]


def test_QRadar_field_name_with_whitespace(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                sel:
                    field name: value
                condition: sel
        """)
    ) == [
               'SELECT * FROM events WHERE "field name"=\'value\''
           ]


def test_QRadar_bool_value(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                sel:
                    field: false
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE field=false"
           ]


def test_QRadar_keywords_query(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                product: test_product
            detection:
                keywords:
                    - keyword1
                    - keyword2
                    - keyword3
                condition: keywords
        """)
    ) == [
        "SELECT * FROM events WHERE LOWER(UTF8(payload)) LIKE 'keyword1' OR LOWER(UTF8("
        "payload)) LIKE 'keyword2' OR LOWER(UTF8(payload)) LIKE 'keyword3'"
    ]


def test_QRadar_in_expression_with_wildcard(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
        title: Test
        status: test
        logsource:
            category: test_category
            product: test_product
        detection:
            sel:
                fieldName:
                    - valueA
                    - valueB
                    - valueC*
            condition: sel
    """)
    ) == ["SELECT * FROM events WHERE fieldName='valueA' OR fieldName='valueB' OR "
          "LOWER(fieldName) LIKE 'valuec%'"]


def test_QRadar_log_sources(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                product: windows
                service: apache
            detection:
                sel:
                    field: value
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE devicetype IN(10, 12) AND field='value'"
           ]


def test_QRadar_identical_log_sources(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                product: windows
                service: windows
            detection:
                sel:
                    field: value
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE devicetype=12 AND field='value'"
           ]


def test_QRadar_single_log_source(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                service: test_service
                product: windows
            detection:
                sel:
                    field: value
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE devicetype=12 AND field='value'"
           ]


def test_QRadar_escaping_value(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                service: test_service
            detection:
                sel:
                    field: value'
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE field='value'''"
           ]


def test_QRadar_escaping_keyword(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                service: test_service
            detection:
                keywords:
                    - keyword'
                condition: keywords
        """)
    ) == [
               "SELECT * FROM events WHERE LOWER(UTF8(payload)) LIKE 'keyword'''"
           ]


def test_QRadar_escaping_regex(QRadar_backend: QRadarAQLBackend):
    assert QRadar_backend.convert(
        SigmaCollection.from_yaml("""
            title: Test
            status: test
            logsource:
                category: test_category
                service: test_service
            detection:
                sel:
                    Command|re: ".[a-zA-Z0-9]{1,6}.[ |']{1}"
                condition: sel
        """)
    ) == [
               "SELECT * FROM events WHERE Command MATCHES '.[a-zA-Z0-9]{1,"
               "6}.[ |'']{1}'"
           ]
