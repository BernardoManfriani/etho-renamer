"""Test unitari — core, validation, UndoManager, resolve_input, pup list."""
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from etho_renamer.validation import (
    normalize_pup, normalize_mama_name, normalize_month,
    normalize_year, normalize_initials, normalize_part,
)
from etho_renamer.core import (
    parse_prefix_date, compute_new_filename, resolve_input,
    apply_pup_list, determine_activity, extract_observation_from_file,
)
from etho_renamer.models import FileInfo, InputData, InputOverrides, RenameOperation, UndoManager
from etho_renamer.config import MONTHS


# ══════════════════════════════════════════════════════════════════════════════
#  Validation
# ══════════════════════════════════════════════════════════════════════════════

class TestValidation:
    """Test validazione input."""

    def test_normalize_pup_valid(self):
        result, err = normalize_pup("pup4")
        assert result == "pup4"
        assert err is None

    def test_normalize_pup_uppercase(self):
        result, err = normalize_pup("PUP4")
        assert result == "pup4"
        assert err is None

    def test_normalize_pup_invalid(self):
        result, err = normalize_pup("invalid")
        assert result == ""
        assert err is not None

    def test_normalize_mama_valid(self):
        result, err = normalize_mama_name("Nova")
        assert result == "Nova"
        assert err is None

    def test_normalize_mama_with_spaces(self):
        result, err = normalize_mama_name("Nova Blue")
        assert result == "Nova-Blue"
        assert err is not None  # warning

    def test_normalize_month_abbreviation(self):
        result, err = normalize_month("jan", MONTHS)
        assert result == "jan"
        assert err is None

    def test_normalize_month_full(self):
        result, err = normalize_month("january", MONTHS)
        assert result == "jan"
        assert err is None

    def test_normalize_month_invalid(self):
        result, err = normalize_month("invalid", MONTHS)
        assert result == ""
        assert err is not None

    def test_normalize_year_2digits(self):
        result, err = normalize_year("26")
        assert result == "26"
        assert err is None

    def test_normalize_year_4digits(self):
        result, err = normalize_year("2026")
        assert result == "26"
        assert err is None

    def test_normalize_year_invalid(self):
        result, err = normalize_year("abc")
        assert result == ""
        assert err is not None

    def test_normalize_initials_valid(self):
        result, err = normalize_initials("IM")
        assert result == "IM"
        assert err is None

    def test_normalize_initials_lowercase(self):
        result, err = normalize_initials("im")
        assert result == "IM"
        assert err is None

    def test_normalize_initials_too_long(self):
        result, err = normalize_initials("IMLONG")
        assert result == ""
        assert err is not None

    def test_normalize_part_valid(self):
        result, err = normalize_part("Part1")
        assert result == "Part1"
        assert err is None

    def test_normalize_part_lowercase(self):
        result, err = normalize_part("part1")
        assert result == "Part1"
        assert err is None

    def test_normalize_part_invalid(self):
        result, err = normalize_part("invalid")
        assert result == ""
        assert err is not None


# ══════════════════════════════════════════════════════════════════════════════
#  Parsing
# ══════════════════════════════════════════════════════════════════════════════

class TestParsing:
    """Test parsing filename."""

    def test_parse_prefix_date_valid(self):
        result = parse_prefix_date("20260202_qualcosa.MTS")
        assert result == (2026, 2, 2)

    def test_parse_prefix_date_invalid_date(self):
        result = parse_prefix_date("20261313_qualcosa.MTS")
        assert result is None

    def test_parse_prefix_date_no_prefix(self):
        result = parse_prefix_date("qualcosa.MTS")
        assert result is None


# ══════════════════════════════════════════════════════════════════════════════
#  Compute Filename
# ══════════════════════════════════════════════════════════════════════════════

class TestComputeFilename:
    """Test costruzione nuovo filename."""

    def test_compute_new_filename_no_prefix(self):
        mtime = datetime(2026, 2, 2, 12, 30, 0)
        file_info = FileInfo(
            path=Path("test.mts"),
            original_filename="test.mts",
            extension=".mts",
            mtime=mtime,
        )
        input_data = InputData(
            pup="pup4", mama_name="Nova", month="feb",
            year="26", initials="IM", part="Part1",
        )
        new_name, err = compute_new_filename(file_info, input_data, 600)
        assert err == ""
        assert new_name == "20260202_pup4_Nova_feb_26_1220_Part1_IM.mts"

    def test_compute_new_filename_with_prefix(self):
        mtime = datetime(2026, 2, 2, 12, 30, 0)
        file_info = FileInfo(
            path=Path("20260101_qualcosa.mts"),
            original_filename="20260101_qualcosa.mts",
            extension=".mts",
            mtime=mtime,
        )
        input_data = InputData(
            pup="pup4", mama_name="Nova", month="jan",
            year="26", initials="IM", part="Part1",
        )
        new_name, err = compute_new_filename(file_info, input_data, 600)
        assert err == ""
        assert new_name == "20260101_pup4_Nova_jan_26_1220_Part1_IM.mts"

    def test_compute_new_filename_no_duration(self):
        file_info = FileInfo(
            path=Path("test.mts"),
            original_filename="test.mts",
            extension=".mts",
            mtime=datetime.now(),
        )
        input_data = InputData(
            pup="pup4", mama_name="Nova", month="feb",
            year="26", initials="IM", part="Part1",
        )
        new_name, err = compute_new_filename(file_info, input_data, None)
        assert new_name is None
        assert "Durata" in err

    def test_compute_new_filename_no_part(self):
        mtime = datetime(2026, 3, 15, 10, 0, 0)
        file_info = FileInfo(
            path=Path("test.mts"),
            original_filename="test.mts",
            extension=".mts",
            mtime=mtime,
        )
        input_data = InputData(
            pup="pup1", mama_name="Luna", month="mar",
            year="26", initials="AB", part="",
        )
        new_name, err = compute_new_filename(file_info, input_data, 300)
        assert err == ""
        assert "Part" not in new_name
        assert new_name == "20260315_pup1_Luna_mar_26_0955_AB.mts"


# ══════════════════════════════════════════════════════════════════════════════
#  resolve_input
# ══════════════════════════════════════════════════════════════════════════════

class TestResolveInput:
    """Test merge global input + override."""

    def _base_input(self):
        return InputData(
            pup="pup1", mama_name="Nova", month="jan",
            year="26", initials="IM", part="",
        )

    def test_override_pup(self):
        base = self._base_input()
        ov = InputOverrides(pup="pup4")
        result = resolve_input(base, ov)
        assert result.pup == "pup4"
        assert result.mama_name == "Nova"  # inherited

    def test_override_mama(self):
        base = self._base_input()
        ov = InputOverrides(mama_name="Luna")
        result = resolve_input(base, ov)
        assert result.mama_name == "Luna"
        assert result.pup == "pup1"  # inherited

    def test_override_none_inherits(self):
        base = self._base_input()
        ov = InputOverrides()  # tutti None
        result = resolve_input(base, ov)
        assert result.pup == base.pup
        assert result.mama_name == base.mama_name
        assert result.month == base.month
        assert result.year == base.year
        assert result.initials == base.initials
        assert result.part == base.part

    def test_override_all_fields(self):
        base = self._base_input()
        ov = InputOverrides(
            pup="pup5", mama_name="Stella", month="feb",
            year="27", initials="XY", part="Part2",
        )
        result = resolve_input(base, ov)
        assert result.pup == "pup5"
        assert result.mama_name == "Stella"
        assert result.month == "feb"
        assert result.year == "27"
        assert result.initials == "XY"
        assert result.part == "Part2"


# ══════════════════════════════════════════════════════════════════════════════
#  UndoManager
# ══════════════════════════════════════════════════════════════════════════════

class TestUndoManager:
    """Test undo/rollback operazioni di rename."""

    def setup_method(self):
        """Crea directory temporanea per i test."""
        self.tmpdir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Rimuove directory temporanea."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_file(self, name: str) -> Path:
        p = self.tmpdir / name
        p.write_text("dummy content")
        return p

    def test_can_undo_empty(self):
        mgr = UndoManager()
        assert not mgr.can_undo()

    def test_push_enables_undo(self):
        mgr = UndoManager()
        from_p = self.tmpdir / "original.mts"
        to_p = self.tmpdir / "renamed.mts"
        op = RenameOperation(from_path=from_p, to_path=to_p, timestamp=datetime.now())
        mgr.push_transaction([op])
        assert mgr.can_undo()

    def test_undo_rename_ok(self):
        """Rename reale + undo: file torna al nome originale."""
        original = self._make_file("original.mts")
        renamed = self.tmpdir / "renamed.mts"

        # Esegui rename manuale
        original.rename(renamed)
        assert renamed.exists()
        assert not original.exists()

        mgr = UndoManager()
        op = RenameOperation(
            from_path=original,
            to_path=renamed,
            timestamp=datetime.now(),
        )
        mgr.push_transaction([op])

        results = mgr.undo_last()
        assert len(results) == 1
        undo_op, err = results[0]
        assert err == "", f"Errore inatteso: {err}"
        assert original.exists()
        assert not renamed.exists()

    def test_undo_fails_if_target_missing(self):
        """Undo fallisce se il file rinominato non esiste più."""
        mgr = UndoManager()
        op = RenameOperation(
            from_path=self.tmpdir / "original.mts",
            to_path=self.tmpdir / "ghost.mts",  # non esiste
            timestamp=datetime.now(),
        )
        mgr.push_transaction([op])
        results = mgr.undo_last()
        _, err = results[0]
        assert err != ""  # deve avere errore

    def test_undo_fails_if_original_occupied(self):
        """Undo fallisce se il nome originale è già occupato da altro file."""
        renamed = self._make_file("renamed.mts")
        occupied = self._make_file("original.mts")  # occupa il nome originale

        mgr = UndoManager()
        op = RenameOperation(
            from_path=occupied,     # stesso path: non dovrebbe essere un problema
            to_path=renamed,
            timestamp=datetime.now(),
        )
        # Caso critico: from_path e to_path diversi, ma from_path esiste già
        from_other = self.tmpdir / "other_original.mts"
        op2 = RenameOperation(
            from_path=occupied,     # occupied esiste
            to_path=renamed,
            timestamp=datetime.now(),
        )
        mgr.push_transaction([op2])
        results = mgr.undo_last()
        _, err = results[0]
        # from_path esiste, ma è diverso da to_path: deve segnalare errore
        assert err != ""

    def test_undo_stack_pops_last(self):
        """Stack LIFO: undo_last rimuove l'ultimo batch."""
        f1 = self._make_file("f1_orig.mts")
        r1 = self.tmpdir / "f1_new.mts"
        f1.rename(r1)

        f2 = self._make_file("f2_orig.mts")
        r2 = self.tmpdir / "f2_new.mts"
        f2.rename(r2)

        mgr = UndoManager()
        op1 = RenameOperation(from_path=f1, to_path=r1, timestamp=datetime.now())
        op2 = RenameOperation(from_path=f2, to_path=r2, timestamp=datetime.now())
        mgr.push_transaction([op1])
        mgr.push_transaction([op2])

        assert mgr.can_undo()
        results = mgr.undo_last()  # annulla batch 2 (f2)
        assert len(results) == 1
        undo_op, err = results[0]
        assert undo_op.from_path == f2
        assert err == ""
        assert f2.exists()

        assert mgr.can_undo()  # rimane batch 1
        results2 = mgr.undo_last()
        assert not mgr.can_undo()


# ══════════════════════════════════════════════════════════════════════════════
#  apply_pup_list
# ══════════════════════════════════════════════════════════════════════════════

class TestApplyPupList:
    """Test assegnazione sequenziale pup."""

    def test_basic_assignment(self):
        result = apply_pup_list(4, ["pup1", "pup4", "pup1", "pup5"])
        assert result == {0: "pup1", 1: "pup4", 2: "pup1", 3: "pup5"}

    def test_list_shorter_than_files(self):
        result = apply_pup_list(5, ["pup1", "pup2"])
        assert result == {0: "pup1", 1: "pup2"}
        assert 2 not in result
        assert 3 not in result

    def test_list_longer_than_files(self):
        result = apply_pup_list(2, ["pup1", "pup2", "pup3", "pup4"])
        assert result == {0: "pup1", 1: "pup2"}

    def test_empty_list(self):
        result = apply_pup_list(3, [])
        assert result == {}

    def test_empty_files(self):
        result = apply_pup_list(0, ["pup1", "pup2"])
        assert result == {}


# ══════════════════════════════════════════════════════════════════════════════
#  determine_activity
# ══════════════════════════════════════════════════════════════════════════════

class TestDetermineActivity:
    """Test regola Activity basata su durata."""

    def test_15min_exact_is_full(self):
        assert determine_activity(15 * 60) == "Full"

    def test_over_15min_is_full(self):
        assert determine_activity(20 * 60) == "Full"

    def test_under_15min_is_sleep(self):
        assert determine_activity(7 * 60 + 30) == "sleep"

    def test_just_under_15min_is_sleep(self):
        assert determine_activity(15 * 60 - 1) == "sleep"

    def test_zero_is_sleep(self):
        assert determine_activity(0) == "sleep"


# ══════════════════════════════════════════════════════════════════════════════
#  extract_observation_from_file — part number
# ══════════════════════════════════════════════════════════════════════════════

class TestExtractObservation:
    """Test estrazione osservazione da nome file, con cattura PartN."""

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_file(self, name: str) -> Path:
        p = self.tmpdir / name
        p.write_text("dummy")
        return p

    def test_part1_fills_part1_column(self):
        fp = self._make_file("20260212_pup4_Nova_feb_26_1020_Part1_IM.mts")
        obs = extract_observation_from_file(fp, 7 * 60 + 30, 1)
        assert obs is not None
        assert obs.part1 == "7'30"
        assert obs.part2 == ""

    def test_part2_fills_part2_column(self):
        fp = self._make_file("20260212_pup4_Nova_feb_26_1020_Part2_IM.mts")
        obs = extract_observation_from_file(fp, 6 * 60 + 10, 1)
        assert obs is not None
        assert obs.part1 == ""
        assert obs.part2 == "6'10"

    def test_no_part_fills_part1(self):
        fp = self._make_file("20260212_pup4_Nova_feb_26_1020_IM.mts")
        obs = extract_observation_from_file(fp, 9 * 60, 1)
        assert obs is not None
        assert obs.part1 == "9'00"
        assert obs.part2 == ""

    def test_activity_auto_sleep(self):
        fp = self._make_file("20260212_pup4_Nova_feb_26_1020_Part1_IM.mts")
        obs = extract_observation_from_file(fp, 7 * 60 + 30, 1)
        assert obs.activity == "sleep"

    def test_activity_auto_full(self):
        fp = self._make_file("20260212_pup4_Nova_feb_26_1020_IM.mts")
        obs = extract_observation_from_file(fp, 16 * 60, 1)
        assert obs.activity == "Full"

    def test_full_obs_parts_are_empty(self):
        """Osservazione >= 15 min: nessuna colonna partN viene compilata."""
        fp = self._make_file("20260212_pup4_Nova_feb_26_1020_Part1_IM.mts")
        obs = extract_observation_from_file(fp, 15 * 60, 1)
        assert obs.activity == "Full"
        assert obs.part1 == ""
        assert obs.part2 == ""

    def test_pup_id_format(self):
        fp = self._make_file("20260212_pup4_Nova_feb_26_1020_IM.mts")
        obs = extract_observation_from_file(fp, 300, 1)
        assert obs.pup_id == "pup4_nova_feb_26"

    def test_date_format(self):
        fp = self._make_file("20260212_pup4_Nova_feb_26_1020_IM.mts")
        obs = extract_observation_from_file(fp, 300, 1)
        assert obs.date == "2026/02/12"

    def test_time_format(self):
        fp = self._make_file("20260212_pup4_Nova_feb_26_1020_IM.mts")
        obs = extract_observation_from_file(fp, 300, 1)
        assert obs.time == "10:20"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
