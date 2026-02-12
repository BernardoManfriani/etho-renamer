"""Test unitari."""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from etho_renamer.validation import (
    normalize_pup, normalize_mama_name, normalize_month,
    normalize_year, normalize_initials, normalize_part
)
from etho_renamer.core import parse_prefix_date, compute_new_filename
from etho_renamer.models import FileInfo, InputData
from etho_renamer.config import MONTHS


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


class TestComputeFilename:
    """Test costruzione nuovo filename."""
    
    def test_compute_new_filename_no_prefix(self):
        """Filename senza prefisso data."""
        # Mock FileInfo
        mtime = datetime(2026, 2, 2, 12, 30, 0)  # 2026-02-02 12:30
        file_info = FileInfo(
            path=Path("test.mts"),
            original_filename="test.mts",
            extension=".mts",
            mtime=mtime
        )
        
        # Mock InputData
        input_data = InputData(
            pup="pup4",
            mama_name="Nova",
            month="feb",
            year="26",
            initials="IM",
            part="Part1"
        )
        
        # Durata 10 minuti = 600 secondi
        # Start time: 2026-02-02 12:20 (12:30 - 10 min)
        duration = 600
        
        new_name, err = compute_new_filename(file_info, input_data, duration)
        
        assert err == ""
        assert new_name == "20260202_pup4_Nova_feb_26_1220_Part1_IM.mts"
    
    def test_compute_new_filename_with_prefix(self):
        """Filename con prefisso data: usa data dal prefisso."""
        # mtime: 2026-02-02 12:30
        # filename ha prefisso 20260101 (gennaio)
        # Atteso: YYYYMMDD = 20260101 (dal prefisso), HHMM = 12:20 (da mtime - durata)
        mtime = datetime(2026, 2, 2, 12, 30, 0)
        file_info = FileInfo(
            path=Path("20260101_qualcosa.mts"),
            original_filename="20260101_qualcosa.mts",
            extension=".mts",
            mtime=mtime
        )
        
        input_data = InputData(
            pup="pup4",
            mama_name="Nova",
            month="jan",
            year="26",
            initials="IM",
            part="Part1"
        )
        
        duration = 600  # 10 minuti
        
        new_name, err = compute_new_filename(file_info, input_data, duration)
        
        assert err == ""
        # YYYYMMDD viene dal prefisso (20260101), ora da mtime - durata = 12:20
        assert new_name == "20260101_pup4_Nova_jan_26_1220_Part1_IM.mts"
    
    def test_compute_new_filename_no_duration(self):
        """Test con durata mancante."""
        file_info = FileInfo(
            path=Path("test.mts"),
            original_filename="test.mts",
            extension=".mts",
            mtime=datetime.now()
        )
        
        input_data = InputData(
            pup="pup4",
            mama_name="Nova",
            month="feb",
            year="26",
            initials="IM",
            part="Part1"
        )
        
        new_name, err = compute_new_filename(file_info, input_data, None)
        
        assert new_name is None
        assert "Durata" in err


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
