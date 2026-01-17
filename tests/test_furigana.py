import pytest
from ankicard.core.furigana import to_hiragana, get_furigana, get_tokenizer


class TestToHiragana:
    """Tests for katakana to hiragana conversion."""

    def test_katakana_to_hiragana(self, sample_katakana, sample_hiragana):
        """Test basic katakana to hiragana conversion."""
        result = to_hiragana(sample_katakana)
        assert result == sample_hiragana

    def test_mixed_text_preserves_non_katakana(self):
        """Test that non-katakana characters are preserved."""
        text = "ABCカタカナ123"
        result = to_hiragana(text)
        assert result == "ABCかたかな123"

    def test_empty_string(self):
        """Test empty string handling."""
        assert to_hiragana("") == ""

    def test_hiragana_unchanged(self):
        """Test that hiragana is not affected."""
        hiragana = "ひらがな"
        assert to_hiragana(hiragana) == hiragana

    def test_full_katakana_range(self):
        """Test conversion across full katakana range."""
        # Test a few key characters
        assert to_hiragana("ア") == "あ"
        assert to_hiragana("ン") == "ん"
        assert to_hiragana("ガ") == "が"


class TestGetFurigana:
    """Tests for furigana generation."""

    def test_simple_kanji(self):
        """Test furigana generation for simple kanji."""
        result = get_furigana("日本語")
        assert "日本語[にほんご]" in result

    def test_mixed_kanji_hiragana(self, sample_japanese_with_kanji):
        """Test furigana with mixed kanji and hiragana."""
        result = get_furigana(sample_japanese_with_kanji)
        # Should contain furigana for kanji but not hiragana
        assert "[" in result
        assert "]" in result

    def test_only_hiragana(self):
        """Test that pure hiragana text has no furigana."""
        result = get_furigana("ひらがな")
        assert "[" not in result
        assert "]" not in result
        assert result == "ひらがな"

    def test_empty_string(self):
        """Test empty string handling."""
        result = get_furigana("")
        assert result == ""

    def test_kanji_with_correct_furigana_format(self):
        """Test that furigana follows Anki format: 漢字[かんじ]"""
        result = get_furigana("学生")
        assert "学生[" in result
        assert "]" in result
        # Should be hiragana in brackets
        assert "がくせい" in result

    def test_particles_no_furigana(self):
        """Test that particles don't get furigana."""
        result = get_furigana("私は")
        # は should not get furigana
        parts = result.split()
        assert any("私[" in part for part in parts)


class TestGetTokenizer:
    """Tests for tokenizer singleton."""

    def test_tokenizer_singleton(self):
        """Test that get_tokenizer returns the same instance."""
        tokenizer1 = get_tokenizer()
        tokenizer2 = get_tokenizer()
        assert tokenizer1 is tokenizer2

    def test_tokenizer_is_functional(self):
        """Test that tokenizer can tokenize text."""
        tokenizer = get_tokenizer()
        tokens = list(tokenizer.tokenize("日本語"))
        assert len(tokens) > 0


class TestMixedKanjiKanaFurigana:
    """Tests for furigana generation with mixed kanji and kana words."""

    def test_basic_i_adjective_kibishii(self):
        """Test basic i-adjective: 厳しい → 厳[きび]しい"""
        result = get_furigana("厳しい")
        assert result == "厳[きび]しい"

    def test_basic_i_adjective_ookii(self):
        """Test basic i-adjective: 大きい → 大[おお]きい"""
        result = get_furigana("大きい")
        assert result == "大[おお]きい"

    def test_basic_i_adjective_chiisai(self):
        """Test basic i-adjective: 小さい → 小[ちい]さい"""
        result = get_furigana("小さい")
        assert result == "小[ちい]さい"

    def test_basic_i_adjective_atarashii(self):
        """Test basic i-adjective: 新しい → 新[あたら]しい"""
        result = get_furigana("新しい")
        assert result == "新[あたら]しい"

    def test_basic_i_adjective_furui(self):
        """Test basic i-adjective: 古い → 古[ふる]い"""
        result = get_furigana("古い")
        assert result == "古[ふる]い"

    def test_complex_adjective_omoshiroi(self):
        """Test complex adjective: 面白い → 面白[おもしろ]い"""
        result = get_furigana("面白い")
        assert result == "面白[おもしろ]い"

    def test_complex_adjective_utsukushii(self):
        """Test complex adjective: 美しい → 美[うつく]しい"""
        result = get_furigana("美しい")
        assert result == "美[うつく]しい"

    def test_complex_adjective_tanoshii(self):
        """Test complex adjective: 楽しい → 楽[たの]しい"""
        result = get_furigana("楽しい")
        assert result == "楽[たの]しい"

    def test_verb_taberu(self):
        """Test ichidan verb: 食べる → 食[た]べる"""
        result = get_furigana("食べる")
        assert result == "食[た]べる"

    def test_verb_miru(self):
        """Test ichidan verb: 見る → 見[み]る"""
        result = get_furigana("見る")
        assert result == "見[み]る"

    def test_verb_iku(self):
        """Test godan verb: 行く → 行[い]く"""
        result = get_furigana("行く")
        assert result == "行[い]く"

    def test_verb_yomu(self):
        """Test godan verb: 読む → 読[よ]む"""
        result = get_furigana("読む")
        assert result == "読[よ]む"

    def test_verb_kaku(self):
        """Test godan verb: 書く → 書[か]く"""
        result = get_furigana("書く")
        assert result == "書[か]く"

    def test_verb_hanasu(self):
        """Test godan verb: 話す → 話[はな]す"""
        result = get_furigana("話す")
        assert result == "話[はな]す"

    def test_word_with_leading_kana_onegai(self):
        """Test word with leading kana: お願い → お願[ねが]い"""
        result = get_furigana("お願い")
        assert result == "お願[ねが]い"

    def test_word_with_leading_kana_gohan(self):
        """Test word with leading kana: ご飯 → ご飯[はん]"""
        result = get_furigana("ご飯")
        assert result == "ご飯[はん]"

    def test_word_with_leading_kana_ocha(self):
        """Test word with leading kana: お茶 → お茶[ちゃ]"""
        result = get_furigana("お茶")
        assert result == "お茶[ちゃ]"

    def test_edge_case_short_okurigana(self):
        """Test single kanji with short okurigana: 行く → 行[い]く"""
        result = get_furigana("行く")
        assert result == "行[い]く"

    def test_edge_case_irregular_verb_kuru(self):
        """Test irregular verb: 来る → 来[く]る"""
        result = get_furigana("来る")
        assert result == "来[く]る"

    def test_edge_case_kiku(self):
        """Test verb with potential reading ambiguity: 聞く → 聞[き]く"""
        result = get_furigana("聞く")
        assert result == "聞[き]く"

    def test_edge_case_kanji_only_noun(self):
        """Test kanji-only noun: 話 → 話[はなし]"""
        result = get_furigana("話")
        assert result == "話[はなし]"

    def test_all_kanji_nihongo(self):
        """Test all-kanji word: 日本語 → 日本語[にほんご]"""
        result = get_furigana("日本語")
        assert "日本語[にほんご]" in result

    def test_all_kanji_gakusei(self):
        """Test all-kanji word: 学生 → 学生[がくせい]"""
        result = get_furigana("学生")
        assert "学生[がくせい]" in result

    def test_all_kanji_sensei(self):
        """Test all-kanji word: 先生 → 先生[せんせい]"""
        result = get_furigana("先生")
        assert "先生[せんせい]" in result

    def test_all_hiragana_unchanged(self):
        """Test all-hiragana word has no furigana: ひらがな → ひらがな"""
        result = get_furigana("ひらがな")
        assert "[" not in result
        assert "]" not in result
        assert result == "ひらがな"

    def test_all_katakana_unchanged(self):
        """Test all-katakana word has no furigana: カタカナ → カタカナ"""
        result = get_furigana("カタカナ")
        assert "[" not in result
        assert "]" not in result

    def test_full_sentence_with_mixed_words(self):
        """Test full sentence: 天気が厳しい。"""
        result = get_furigana("天気が厳しい。")
        # Should contain both all-kanji and mixed words
        assert "天気[てんき]" in result
        assert "厳[きび]しい" in result

    def test_full_sentence_complex(self):
        """Test complex sentence: 私は日本語を勉強しています。"""
        result = get_furigana("私は日本語を勉強しています。")
        # Should have furigana for kanji words
        assert "[" in result
        assert "]" in result
        # Particles should not have furigana
        assert "は" in result
        assert "を" in result
