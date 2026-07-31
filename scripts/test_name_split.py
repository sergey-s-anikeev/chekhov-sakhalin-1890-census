import argparse
import unittest
from pathlib import Path

from name_split import load_exceptions, load_lexicon, parse_one


HERE = Path(__file__).parent
COLS = argparse.Namespace(name="name_raw", sex="sex", religion="religion", person_id="person_id")


class NameSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexicon = load_lexicon(HERE / "name_lexicon.csv")
        cls.exceptions = load_exceptions(HERE / "name_split_exceptions.csv")
        for path in (
            HERE / "name_split_muslim_review_all_20260723.csv",
            HERE / "name_split_patronymic_review_exceptions_20260723.csv",
            HERE / "name_split_first_name_review_exceptions_20260723.csv",
            HERE / "name_split_ambiguous_review_exceptions_20260723.csv",
        ):
            additions = load_exceptions(path)
            overlap = set(cls.exceptions) & set(additions)
            if overlap:
                raise ValueError("duplicate test exception IDs: " + ", ".join(sorted(overlap)))
            cls.exceptions.update(additions)

    def parse(self, name, sex="Мужской", religion="Православное", person_id=""):
        return parse_one({"person_id": person_id, "name_raw": name, "name_alias": "",
                          "sex": sex, "religion": religion},
                         COLS, self.lexicon, self.exceptions)

    def test_standard_first_patronymic_last(self):
        got = self.parse("Сергей Иванов Петров")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Сергей", "Иванов", "Петров"))

    def test_two_token_source_order_does_not_require_lexicon(self):
        got = self.parse("Ценер Гамчурин")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Ценер", "", "Гамчурин"))
        self.assertEqual(got["parse_status"], "observed")

    def test_last_first_order_when_only_second_is_curated_first(self):
        got = self.parse("Былошицкая Ирина Степанова", sex="Женский")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Ирина", "Степанова", "Былошицкая"))
        self.assertEqual(got["name_order_detected"], "last_first_patronymic")

    def test_ordinal_is_ignored_for_structure(self):
        got = self.parse("Иван 2-й Трофимов Лузин")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Иван", "Трофимов", "Лузин"))

    def test_single_first_name_is_not_family_enriched(self):
        got = self.parse("Дорофей")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Дорофей", "", ""))
        self.assertNotIn("inferred", " ".join(got.values()))

    def test_unknown_single_token_is_tentative_surname(self):
        got = self.parse("Скрупский")
        self.assertEqual(got["last_name"], "Скрупский")
        self.assertEqual(got["parse_status"], "ambiguous")

    def test_unnamed_descriptor_is_last_name(self):
        got = self.parse("Некрещеная", sex="Женский")
        self.assertEqual(got["last_name"], "Некрещеная")
        self.assertEqual(got["parse_status"], "observed")

    def test_complex_muslim_name_is_manual(self):
        got = self.parse("Оглы Юсуф Ага-Киши", religion="Магометанское")
        self.assertEqual(got["parse_status"], "manual_review")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("", "", ""))

    def test_simple_two_token_muslim_name_uses_first_last(self):
        got = self.parse("Курбан Алиев", religion="Магометанское")
        self.assertEqual((got["first_name"], got["last_name"]),
                         ("Курбан", "Алиев"))

    def test_second_russian_given_name_proposes_patronymic_for_review(self):
        got = self.parse("Федор Иван Храпылин")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Федор", "", "Храпылин"))
        self.assertEqual(got["patronymic_name_proposed"], "Иванов")
        self.assertEqual(got["parse_status"], "manual_review")

    def test_hyphenated_two_token_muslim_name_requires_review(self):
        got = self.parse("Оглы-Мамет Тали-Кербалай", religion="Магометанское")
        self.assertEqual(got["parse_status"], "manual_review")
        self.assertEqual(got["parse_rule"], "hyphenated_two_token_muslim_manual")
        self.assertEqual(
            (got["first_name"], got["patronymic_name"], got["last_name"]),
            ("", "", ""),
        )

    def test_reviewed_polish_double_first_name(self):
        got = self.parse("Наполеон Станислав Лисовский", religion="Католическое",
                         person_id="P000760")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Наполеон Станислав", "", "Лисовский"))

    def test_unreviewed_catholic_double_given_name_has_no_russian_patronymic_proposal(self):
        got = self.parse("Ян Генрих Биндер", religion="Католическое")
        self.assertEqual(got["parse_status"], "manual_review")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Ян Генрих", "", "Биндер"))
        self.assertEqual(got["patronymic_name_proposed"], "")
        self.assertEqual(got["manual_review_reason"], "verify_catholic_lutheran_compound_given_name")

    def test_catholic_russianized_patronymic_is_retained(self):
        got = self.parse("Елена Францова Шляхова", sex="Женский", religion="Католическое")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Елена", "Францова", "Шляхова"))
        self.assertEqual(got["parse_rule"], "catholic_lutheran_patronymic")

    def test_lutheran_three_token_source_order_is_not_reversed_by_lexicon(self):
        got = self.parse("Замель Ян Радзин", religion="Лютеранское")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Замель Ян", "", "Радзин"))
        self.assertEqual(got["parse_status"], "manual_review")

    def test_catholic_two_token_source_order_is_not_reversed_by_lexicon(self):
        got = self.parse("Рарица Марина", sex="Женский", religion="Католическое")
        self.assertEqual((got["first_name"], got["last_name"]), ("Рарица", "Марина"))

    def test_reviewed_triple_first_name(self):
        got = self.parse("Август Вильгельм Генрих Меллартек", religion="Лютеранское",
                         person_id="P001550")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Август Вильгельм Генрих", "", "Меллартек"))

    def test_reviewed_korean_chinese_compound_surname(self):
        got = self.parse("Пен-Оги-Цой", religion="", person_id="P002141")
        self.assertEqual((got["first_name"], got["last_name"]), ("", "Пен-Оги-Цой"))

    def test_reviewed_alias_can_be_primary(self):
        row = {"person_id": "P004448", "name_raw": "Консультана Копкиева",
               "name_alias": "Пелагея Васильева", "sex": "Женский",
               "religion": "Православное"}
        got = parse_one(row, COLS, self.lexicon, self.exceptions)
        self.assertEqual((got["first_name"], got["last_name"]), ("Пелагея", "Васильева"))

    def test_unreviewed_four_semantic_tokens_are_manual(self):
        got = self.parse("Мац Иоганов Лектор Лехтола", religion="Лютеранское")
        self.assertEqual(got["parse_status"], "manual_review")
        self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                         ("Мац Иоганов Лектор", "", "Лехтола"))

    def test_reviewed_catholic_lutheran_sample_corrections(self):
        cases = [
            ("P000576", "Ян Генрих Биндер", "Католическое", "Ян Генрих", "Биндер"),
            ("P001351", "Замель Ян Радзин", "Лютеранское", "Замель Ян", "Радзин"),
            ("P005169", "Мац Иоганов Лектор Лехтола", "Лютеранское", "Мац Иоганов Лектор", "Лехтола"),
        ]
        for person_id, name, religion, first, last in cases:
            got = self.parse(name, religion=religion, person_id=person_id)
            self.assertEqual((got["first_name"], got["patronymic_name"], got["last_name"]),
                             (first, "", last))
            self.assertEqual(got["parse_status"], "observed")

    def test_latest_owner_review_exceptions_round_trip(self):
        for path in (
            HERE / "name_split_patronymic_review_exceptions_20260723.csv",
            HERE / "name_split_first_name_review_exceptions_20260723.csv",
            HERE / "name_split_ambiguous_review_exceptions_20260723.csv",
        ):
            reviewed = load_exceptions(path)
            for person_id, expected in reviewed.items():
                got = self.parse(expected["match_name_raw"], person_id=person_id)
                self.assertEqual(
                    (got["first_name"], got["patronymic_name"], got["last_name"]),
                    (expected["first_name"], expected["patronymic_name"], expected["last_name"]),
                )
                self.assertEqual(got["parse_status"], "observed")


if __name__ == "__main__":
    unittest.main()
