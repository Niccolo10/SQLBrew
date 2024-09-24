import math
import unittest

from constraint_oracle import ConstraintOracle
from db.db_connector import connect_to_mysql, load_db_config


class TestConstraintOracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = load_db_config()
        cls.cnx = connect_to_mysql(config)
        cls.cursor = cls.cnx.cursor()
        cls.oracle = ConstraintOracle()

    @classmethod
    def tearDownClass(cls):
        cls.cursor.close()
        cls.cnx.close()

    def setUp(self):
        self.cursor.execute("DROP TABLE IF EXISTS t1;")
        self.cnx.commit()

    def create_table(self, create_statement):
        try:
            self.cursor.execute("DROP TABLE IF EXISTS t1;")
            self.cnx.commit()
            self.cursor.execute(create_statement)
            self.cnx.commit()
            print("Table created successfully.")
        except Exception as e:
            print(f"Failed to create table: {e}")

    # ------------------------------------------------------------------------------------
    # Test cases for INT data type
    # ------------------------------------------------------------------------------------

    def test_int_equal(self):
        # = operator tests
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = 5));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 6), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "6"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5a"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5.0),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5.15346),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = -5));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -5), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-5"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-6"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-5.0"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -5.15346),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5.213214"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = 'abcd'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd"),
            [(False, "v1", "Type error")],
        )

        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd123"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 123),
            [(False, "v1", "Type error")],
        )
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = 'abc34&\n'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&\n"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1000),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1.345),
            [(False, "v1", "Type error")],
        )
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = TRUE));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", False), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 0),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "1"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "TRUE"),
            [(False, "v1", "Type error")],
        )

    def test_int_greater(self):
        # > operator tests
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > 5));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 6), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 4), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > -5));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 0), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -4), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -6), [(False, "v1")]
        )
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > 'abcd'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcde"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1000),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > 'abc34&\n'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&\t"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > TRUE));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", False), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 10), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "TRUE"),
            [(False, "v1", "Type error")],
        )
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > FALSE));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", False), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 0), [(False, "v1")]
        )

    def test_int_like(self):
        # LIKE operator tests
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE '5'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "55"), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "4"), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE '-5'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-5"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -5),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-55"), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE 'abcd'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE 'abc34&\n'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&\n"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE 'TRUE'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "TRUE"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "FALSE"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE 'FALSE'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "FALSE"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", False),
            [(False, "v1", "Type error")],
        )

    def test_int_exp(self):
        # EXP function with = operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(10)),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 10), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(10)"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP(-10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(-10)),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -10), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(-10)"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP('abc')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP('abc')"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP('abc34&%')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&%"),
            [(False, "v1", "Type error")],
        )

        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP(TRUE)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(1)),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(TRUE)"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP(FALSE)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(0)),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", False), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(FALSE)"),
            [(False, "v1", "Type error")],
        )

        # EXP function with > operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > EXP(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(10) + 1),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(10)),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(10) - 1),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > EXP(-10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(-10) + 1),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(-10)),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(-10) - 1),
            [(False, "v1")],
        )

    def test_int_lower(self):
        # LOWER function with = operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 10), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "10"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "100"), [(False, "v1")]
        )
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER(-10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-10"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-10"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -10),
            [(True, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER('ABC')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "ABC"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER('ABC34')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER(TRUE)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "true"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "false"),
            [(False, "v1", "Type error")],
        )

        # LOWER function with > operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "11"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "10"), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 9),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER(-10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-9"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-10"), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -11),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER('ABC')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER('ABC34')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc35"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER(TRUE)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "true1"),
            [(False, "v1", "Type error")],
        )

    # ------------------------------------------------------------------------------------
    # Test cases for FLOAT data type
    # ------------------------------------------------------------------------------------

    def test_float_equal(self):
        # = operator tests
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = 5.5));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5.5), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 6.5), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5.5"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "6.5"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5.5a"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = -5.5));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -5.5), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5.5), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-5.5"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-6.5"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = 'abcd'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = 'abc34&\n'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&\n"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = TRUE));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", False), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1.0),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 0.0),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "TRUE"),
            [(False, "v1", "Type error")],
        )

    def test_float_greater(self):
        # > operator tests
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > 5.5));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 6.5), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5.5), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 4.5), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > -5.5));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 0.0), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -4.5), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -6.5), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > 'abcd'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcde"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1000.0),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > 'abc34&\n'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&\t"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > TRUE));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1.0), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", False), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 10.0), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "TRUE"),
            [(False, "v1", "Type error")],
        )

    def test_float_like(self):
        # LIKE operator tests
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE '5.5'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5.5"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5.5),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "55"), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "4.5"), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE '-5.5'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-5.5"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -5.5),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-55"), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE 'abcd'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE 'abc34&\n'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&\n"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE 'TRUE'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "TRUE"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "FALSE"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 LIKE 'FALSE'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "FALSE"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", False),
            [(False, "v1", "Type error")],
        )

    def test_float_exp(self):
        # EXP function with = operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(10)),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 10), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(10)"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP(-10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(-10)),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -10), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(-10)"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP('abc')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP('abc')"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP('abc34&%')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&%"),
            [(False, "v1", "Type error")],
        )

        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP(TRUE)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(1)),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(TRUE)"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = EXP(FALSE)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(0)),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", False), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(FALSE)"),
            [(False, "v1", "Type error")],
        )

        # EXP function with > operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > EXP(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(10) + 1),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(10)),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(10) - 1),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > EXP(-10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(-10) + 1),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(-10)),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", math.exp(-10) - 1),
            [(False, "v1")],
        )

    def test_float_lower(self):
        # LOWER function with = operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 10), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "10"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "100"), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER(-10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-10"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-10"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -10),
            [(True, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER('ABC')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "ABC"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER('ABC34')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 = LOWER(TRUE)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "true"),
            [(False, "v1", "Type error")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "false"),
            [(False, "v1", "Type error")],
        )

        # LOWER function with > operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "11"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "10"), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 9),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER(-10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-9"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-10"), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -11),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER('ABC')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER('ABC34')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc35"),
            [(False, "v1", "Type error")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT v1 CHECK (c1 > LOWER(TRUE)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "true1"),
            [(False, "v1", "Type error")],
        )

    # ------------------------------------------------------------------------------------
    # Test cases for VARCHAR data type
    # ------------------------------------------------------------------------------------

    def test_varchar_equal(self):
        # = operator tests
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = 'test'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "test"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "Test"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "testing"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = '5'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5a"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 5.0),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = '-5'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-5"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -5),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-5.0"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = 'abc34&\t'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&\t"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abc34&"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = TRUE));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "TRUE"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "FALSE"),
            [(False, "v1")],
        )

    def test_varchar_greater(self):
        # > operator tests
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 > 'test'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "testing"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "testa"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "test"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 > '5'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "6"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "5a"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "4"), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 > '-5'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "0"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-4"), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-6"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", -5), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-5.0000000000000002"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-6abc"),
            [(True, "v1")],
        )
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 > 'abcd'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcde"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcd"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "abcc"),
            [(False, "v1")],
        )

    def test_varchar_like(self):
        # LIKE operator tests
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 LIKE 'test%'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "test"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "testa"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "testing"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "Test"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 LIKE '%test'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "test"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "atest"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "ztest"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "tes"), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 LIKE '%test%'));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "test"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "atestb"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "ztestx"),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "tes"), [(False, "v1")]
        )

    def test_varchar_exp(self):
        # EXP function with = operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = EXP(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", str(math.exp(10))),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", str(math.exp(10) - 5)),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 10), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "10"), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(10)"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = EXP(-10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", str(math.exp(-10))),
            [(True, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "-10"), [(False, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP(-10)"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = EXP('abc')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "EXP('abc')"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "1"),
            [(False, "v1")],
        )

    def test_varchar_lower(self):
        # LOWER function with = operator
        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = LOWER('TEST')));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "test"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "TEST"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "testing"),
            [(False, "v1")],
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = LOWER(10)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "10"), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 10), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "100"), [(False, "v1")]
        )

        self.create_table(
            "CREATE TABLE t1 (id INT AUTO_INCREMENT PRIMARY KEY, c1 VARCHAR(255), CONSTRAINT v1 CHECK (c1 = LOWER(TRUE)));"
        )
        self.oracle = ConstraintOracle()
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "true"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", True), [(True, "v1")]
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "false"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1.25),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", "1.25"),
            [(False, "v1")],
        )
        self.assertEqual(
            self.oracle.evaluate_value_against_constraints("c1", 1), [(True, "v1")]
        )


if __name__ == "__main__":
    unittest.main()
