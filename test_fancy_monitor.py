"""Tests for fancy_monitor.py

Because fancy_monitor.py contains module-level GUI code (Tk(), load_image(),
draw_dashboard(), root.mainloop()), Tkinter and Pillow are mocked at the
sys.modules level *before* the module is imported so that all tests run in a
headless environment without a real display.
"""

import csv
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, call, mock_open, patch

# ---------------------------------------------------------------------------
# Stub out tkinter and PIL *before* importing fancy_monitor so that the
# module-level GUI calls (root = Tk(), load_image(), draw_dashboard(), …)
# execute safely without a display.
# ---------------------------------------------------------------------------

_tk_mock = MagicMock()
# Provide __all__ so that "from tkinter import *" brings exactly these names
# into fancy_monitor's namespace.
_tk_mock.__all__ = ["Tk", "Canvas", "Label"]

_pil_mock = MagicMock()

sys.modules.setdefault("tkinter", _tk_mock)
sys.modules.setdefault("PIL", _pil_mock)
sys.modules.setdefault("PIL.Image", _pil_mock.Image)
sys.modules.setdefault("PIL.ImageTk", _pil_mock.ImageTk)

import fancy_monitor  # noqa: E402  (must come after mock injection)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(row: list) -> str:
    """Write *row* to a NamedTemporaryFile and return its path."""
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    )
    csv.writer(f).writerow(row)
    f.close()
    return f.name


_SAMPLE_ROW = [
    "-65", "connected",         # SIG1, CONN1
    "-70", "disconnected",      # SIG2, CONN2
    "HomeNetwork", "-55", "3",  # SSID2G, SIG2G, CLIENTS2G
    "HomeNetwork5G", "-60", "5",# SSID5G, SIG5G, CLIENTS5G
    "on", "active",             # BT, GPS
    "40.7128", "-74.0060",      # GPSLAT, GPSLONG
]


# ===========================================================================
# read_data() – CSV file absent
# ===========================================================================

class TestReadDataMissingFile(unittest.TestCase):
    """read_data() returns correct defaults when the CSV does not exist."""

    def setUp(self):
        self._patcher = patch("os.path.exists", return_value=False)
        self._patcher.start()
        self.result = fancy_monitor.read_data()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_dict(self):
        self.assertIsInstance(self.result, dict)

    def test_all_14_keys_present(self):
        expected = {
            "SIG1", "CONN1", "SIG2", "CONN2",
            "SSID2G", "SIG2G", "CLIENTS2G",
            "SSID5G", "SIG5G", "CLIENTS5G",
            "BT", "GPS", "GPSLAT", "GPSLONG",
        }
        self.assertEqual(set(self.result.keys()), expected)

    def test_sig1_is_empty(self):
        self.assertEqual(self.result["SIG1"], "")

    def test_conn1_is_empty(self):
        self.assertEqual(self.result["CONN1"], "")

    def test_sig2_is_empty(self):
        self.assertEqual(self.result["SIG2"], "")

    def test_conn2_is_empty(self):
        self.assertEqual(self.result["CONN2"], "")

    def test_ssid2g_is_empty(self):
        self.assertEqual(self.result["SSID2G"], "")

    def test_sig2g_is_empty(self):
        self.assertEqual(self.result["SIG2G"], "")

    def test_clients2g_default_is_zero_string(self):
        self.assertEqual(self.result["CLIENTS2G"], "0")

    def test_ssid5g_is_empty(self):
        self.assertEqual(self.result["SSID5G"], "")

    def test_sig5g_is_empty(self):
        self.assertEqual(self.result["SIG5G"], "")

    def test_clients5g_default_is_zero_string(self):
        self.assertEqual(self.result["CLIENTS5G"], "0")

    def test_bt_default_is_unavailable(self):
        self.assertEqual(self.result["BT"], "unavailable")

    def test_gps_default_is_unavailable(self):
        self.assertEqual(self.result["GPS"], "unavailable")

    def test_gpslat_is_empty(self):
        self.assertEqual(self.result["GPSLAT"], "")

    def test_gpslong_is_empty(self):
        self.assertEqual(self.result["GPSLONG"], "")


# ===========================================================================
# read_data() – CSV file present
# ===========================================================================

class TestReadDataPresentFile(unittest.TestCase):
    """read_data() parses all 14 CSV fields when the file exists."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = _write_csv(_SAMPLE_ROW)
        with patch.object(fancy_monitor, "CSV_PATH", cls._tmp):
            cls.result = fancy_monitor.read_data()

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls._tmp)

    def test_sig1_parsed(self):
        self.assertEqual(self.result["SIG1"], "-65")

    def test_conn1_parsed(self):
        self.assertEqual(self.result["CONN1"], "connected")

    def test_sig2_parsed(self):
        self.assertEqual(self.result["SIG2"], "-70")

    def test_conn2_parsed(self):
        self.assertEqual(self.result["CONN2"], "disconnected")

    def test_ssid2g_parsed(self):
        self.assertEqual(self.result["SSID2G"], "HomeNetwork")

    def test_sig2g_parsed(self):
        self.assertEqual(self.result["SIG2G"], "-55")

    def test_clients2g_parsed(self):
        self.assertEqual(self.result["CLIENTS2G"], "3")

    def test_ssid5g_parsed(self):
        self.assertEqual(self.result["SSID5G"], "HomeNetwork5G")

    def test_sig5g_parsed(self):
        self.assertEqual(self.result["SIG5G"], "-60")

    def test_clients5g_parsed(self):
        self.assertEqual(self.result["CLIENTS5G"], "5")

    def test_bt_parsed(self):
        self.assertEqual(self.result["BT"], "on")

    def test_gps_parsed(self):
        self.assertEqual(self.result["GPS"], "active")

    def test_gpslat_parsed(self):
        self.assertEqual(self.result["GPSLAT"], "40.7128")

    def test_gpslong_parsed(self):
        self.assertEqual(self.result["GPSLONG"], "-74.0060")

    def test_returns_dict(self):
        self.assertIsInstance(self.result, dict)

    def test_exactly_14_keys(self):
        self.assertEqual(len(self.result), 14)


# ===========================================================================
# load_image()
# ===========================================================================

class TestLoadImage(unittest.TestCase):
    """load_image() opens, optionally resizes, and wraps in PhotoImage."""

    def setUp(self):
        self.mock_img = MagicMock()
        self.mock_resized = MagicMock()
        self.mock_photo = MagicMock()
        self.mock_img.resize.return_value = self.mock_resized

        # Patch Image and ImageTk inside fancy_monitor's namespace
        self._img_p = patch.object(fancy_monitor, "Image")
        self._itk_p = patch.object(fancy_monitor, "ImageTk")
        self.mock_Image = self._img_p.start()
        self.mock_ImageTk = self._itk_p.start()
        self.mock_Image.open.return_value = self.mock_img
        self.mock_ImageTk.PhotoImage.return_value = self.mock_photo

    def tearDown(self):
        self._img_p.stop()
        self._itk_p.stop()

    # -- path resolution ---------------------------------------------------

    def test_opens_file_ending_with_given_name(self):
        fancy_monitor.load_image("test.png")
        opened = self.mock_Image.open.call_args[0][0]
        self.assertTrue(opened.endswith("test.png"))

    def test_opened_path_is_absolute(self):
        fancy_monitor.load_image("icon.png")
        opened = self.mock_Image.open.call_args[0][0]
        self.assertTrue(os.path.isabs(opened))

    def test_opened_path_uses_script_dir(self):
        fancy_monitor.load_image("img.png")
        opened = self.mock_Image.open.call_args[0][0]
        expected_dir = fancy_monitor.SCRIPT_DIR
        self.assertEqual(os.path.dirname(opened), expected_dir)

    # -- resize behaviour --------------------------------------------------

    def test_resize_not_called_when_no_size(self):
        fancy_monitor.load_image("test.png")
        self.mock_img.resize.assert_not_called()

    def test_resize_called_with_provided_size(self):
        fancy_monitor.load_image("test.png", size=(80, 80))
        self.mock_img.resize.assert_called_once()
        args = self.mock_img.resize.call_args[0]
        self.assertEqual(args[0], (80, 80))

    def test_resize_passes_antialias_flag(self):
        fancy_monitor.load_image("test.png", size=(90, 60))
        args = self.mock_img.resize.call_args[0]
        # Second positional arg is Image.ANTIALIAS
        self.assertEqual(args[1], self.mock_Image.ANTIALIAS)

    # -- PhotoImage wrapping -----------------------------------------------

    def test_returns_photo_image(self):
        result = fancy_monitor.load_image("test.png")
        self.assertEqual(result, self.mock_photo)

    def test_photo_image_wraps_original_when_no_size(self):
        fancy_monitor.load_image("test.png")
        self.mock_ImageTk.PhotoImage.assert_called_once_with(self.mock_img)

    def test_photo_image_wraps_resized_when_size_given(self):
        fancy_monitor.load_image("test.png", size=(80, 80))
        self.mock_ImageTk.PhotoImage.assert_called_once_with(self.mock_resized)

    def test_open_called_exactly_once(self):
        fancy_monitor.load_image("test.png", size=(50, 50))
        self.mock_Image.open.assert_called_once()


# ===========================================================================
# Client-count parsing logic  (mirrors draw_dashboard logic)
# ===========================================================================

class TestClientCountParsing(unittest.TestCase):
    """int(val) if val.isdigit() else 0  – edge-case coverage."""

    @staticmethod
    def _parse(val: str) -> int:
        return int(val) if val.isdigit() else 0

    def test_single_digit(self):
        self.assertEqual(self._parse("3"), 3)

    def test_zero(self):
        self.assertEqual(self._parse("0"), 0)

    def test_multi_digit(self):
        self.assertEqual(self._parse("10"), 10)

    def test_large_number(self):
        self.assertEqual(self._parse("999"), 999)

    def test_empty_string_returns_zero(self):
        self.assertEqual(self._parse(""), 0)

    def test_alpha_string_returns_zero(self):
        self.assertEqual(self._parse("abc"), 0)

    def test_float_string_returns_zero(self):
        self.assertEqual(self._parse("3.5"), 0)

    def test_negative_string_returns_zero(self):
        self.assertEqual(self._parse("-1"), 0)

    def test_whitespace_string_returns_zero(self):
        self.assertEqual(self._parse(" "), 0)

    def test_alphanumeric_returns_zero(self):
        self.assertEqual(self._parse("5g"), 0)


# ===========================================================================
# Arc-angle calculation logic  (mirrors draw_dashboard math)
# ===========================================================================

class TestArcAngleCalculation(unittest.TestCase):
    """angle = min(100, clients * 10) * 3.6"""

    @staticmethod
    def _angle(clients: int) -> float:
        return min(100, clients * 10) * 3.6

    def test_zero_clients_gives_zero_angle(self):
        self.assertAlmostEqual(self._angle(0), 0.0)

    def test_one_client(self):
        self.assertAlmostEqual(self._angle(1), 36.0)

    def test_two_clients(self):
        self.assertAlmostEqual(self._angle(2), 72.0)

    def test_five_clients(self):
        self.assertAlmostEqual(self._angle(5), 180.0)

    def test_nine_clients(self):
        self.assertAlmostEqual(self._angle(9), 324.0)

    def test_ten_clients_full_circle(self):
        self.assertAlmostEqual(self._angle(10), 360.0)

    def test_eleven_clients_capped_at_full_circle(self):
        self.assertAlmostEqual(self._angle(11), 360.0)

    def test_hundred_clients_capped_at_full_circle(self):
        self.assertAlmostEqual(self._angle(100), 360.0)

    def test_cap_threshold_is_exactly_ten(self):
        # 10 clients → exactly full circle; 9 is not full
        self.assertEqual(self._angle(10), self._angle(11))
        self.assertLess(self._angle(9), self._angle(10))


# ===========================================================================
# GPS text-formatting logic  (mirrors draw_dashboard logic)
# ===========================================================================

class TestGPSTextFormatting(unittest.TestCase):
    """f"Long: {long or '--'}\\nLat : {lat or '--'}" """

    @staticmethod
    def _gps_text(lat: str, long_: str) -> str:
        return f"Long: {long_ or '--'}\nLat : {lat or '--'}"

    def test_both_coords_shown(self):
        t = self._gps_text("40.7128", "-74.0060")
        self.assertIn("40.7128", t)
        self.assertIn("-74.0060", t)

    def test_empty_lat_shows_placeholder(self):
        t = self._gps_text("", "-74.0060")
        self.assertIn("--", t)
        self.assertNotIn("Lat : \n", t)

    def test_empty_long_shows_placeholder(self):
        t = self._gps_text("40.7128", "")
        self.assertIn("--", t)

    def test_both_empty_shows_two_placeholders(self):
        t = self._gps_text("", "")
        self.assertEqual(t.count("--"), 2)

    def test_has_long_label(self):
        t = self._gps_text("1.0", "2.0")
        self.assertTrue(t.startswith("Long:"))

    def test_has_lat_label(self):
        t = self._gps_text("1.0", "2.0")
        self.assertIn("Lat :", t)

    def test_two_line_format(self):
        t = self._gps_text("1.0", "2.0")
        self.assertEqual(len(t.splitlines()), 2)

    def test_long_on_first_line_lat_on_second(self):
        t = self._gps_text("51.5", "-0.12")
        lines = t.splitlines()
        self.assertIn("-0.12", lines[0])
        self.assertIn("51.5", lines[1])


# ===========================================================================
# Bluetooth text-uppercasing logic  (mirrors draw_dashboard logic)
# ===========================================================================

class TestBTTextFormatting(unittest.TestCase):
    """data['BT'].upper() should produce uppercase status strings."""

    def test_on_uppercased(self):
        self.assertEqual("on".upper(), "ON")

    def test_off_uppercased(self):
        self.assertEqual("off".upper(), "OFF")

    def test_unavailable_uppercased(self):
        self.assertEqual("unavailable".upper(), "UNAVAILABLE")

    def test_already_uppercase_unchanged(self):
        self.assertEqual("ON".upper(), "ON")

    def test_mixed_case_uppercased(self):
        self.assertEqual("On".upper(), "ON")

    def test_active_uppercased(self):
        self.assertEqual("active".upper(), "ACTIVE")


# ===========================================================================
# draw_dashboard() integration
# ===========================================================================

class TestDrawDashboard(unittest.TestCase):
    """Verify canvas and label interactions inside draw_dashboard()."""

    _DEFAULT_DATA = {
        "SIG1": "-65",  "CONN1": "connected",
        "SIG2": "-70",  "CONN2": "disconnected",
        "SSID2G": "MyNet",    "SIG2G": "-55", "CLIENTS2G": "3",
        "SSID5G": "MyNet5G",  "SIG5G": "-60", "CLIENTS5G": "5",
        "BT": "on",  "GPS": "active",
        "GPSLAT": "40.7128", "GPSLONG": "-74.0060",
    }

    def setUp(self):
        _tk_mock.reset_mock()

    def _run(self, overrides=None):
        """Run draw_dashboard() with patched read_data; return mock canvas."""
        data = dict(self._DEFAULT_DATA)
        if overrides:
            data.update(overrides)
        mock_canvas = MagicMock()
        _tk_mock.Canvas.return_value = mock_canvas
        with patch.object(fancy_monitor, "read_data", return_value=data):
            fancy_monitor.draw_dashboard()
        return mock_canvas

    # -- canvas creation ---------------------------------------------------

    def test_canvas_is_created(self):
        self._run()
        _tk_mock.Canvas.assert_called()

    def test_canvas_placed_at_origin(self):
        mock_canvas = self._run()
        mock_canvas.place.assert_called_with(x=0, y=0)

    # -- static text labels -----------------------------------------------

    def test_dashboard_title_drawn(self):
        canvas = self._run()
        calls_str = str(canvas.create_text.call_args_list)
        self.assertIn("WIRELESS DASHBOARD", calls_str)

    def test_wifi_24ghz_label_drawn(self):
        canvas = self._run()
        calls_str = str(canvas.create_text.call_args_list)
        self.assertIn("WI-FI 2.4GHz", calls_str)

    def test_wifi_5ghz_label_drawn(self):
        canvas = self._run()
        calls_str = str(canvas.create_text.call_args_list)
        self.assertIn("WI-FI 5GHz", calls_str)

    # -- client count text ------------------------------------------------

    def test_2g_client_count_text_shown(self):
        canvas = self._run({"CLIENTS2G": "3"})
        calls_str = str(canvas.create_text.call_args_list)
        self.assertIn("Clients Connected: 3", calls_str)

    def test_5g_client_count_text_shown(self):
        canvas = self._run({"CLIENTS5G": "5"})
        calls_str = str(canvas.create_text.call_args_list)
        self.assertIn("Clients Connected: 5", calls_str)

    def test_zero_2g_clients_shown(self):
        canvas = self._run({"CLIENTS2G": "0", "CLIENTS5G": "0"})
        calls_str = str(canvas.create_text.call_args_list)
        # Both 2G and 5G client counts should display 0
        self.assertIn("Clients Connected: 0", calls_str)

    # -- percentage text ---------------------------------------------------

    def test_2g_percentage_text_correct(self):
        canvas = self._run({"CLIENTS2G": "3", "CLIENTS5G": "0"})
        calls_str = str(canvas.create_text.call_args_list)
        self.assertIn("30%", calls_str)

    def test_5g_percentage_text_correct(self):
        canvas = self._run({"CLIENTS2G": "0", "CLIENTS5G": "5"})
        calls_str = str(canvas.create_text.call_args_list)
        self.assertIn("50%", calls_str)

    def test_zero_clients_shows_zero_percent(self):
        canvas = self._run({"CLIENTS2G": "0", "CLIENTS5G": "0"})
        calls_str = str(canvas.create_text.call_args_list)
        self.assertIn("0%", calls_str)

    def test_large_client_count_shows_uncapped_percentage(self):
        # Percentage text is clients*10%, arc angle is capped but text is not
        canvas = self._run({"CLIENTS2G": "15", "CLIENTS5G": "0"})
        calls_str = str(canvas.create_text.call_args_list)
        self.assertIn("150%", calls_str)

    # -- arc (donut) drawing ----------------------------------------------

    def test_arc_drawn_for_nonzero_2g_clients(self):
        canvas = self._run({"CLIENTS2G": "5", "CLIENTS5G": "0"})
        canvas.create_arc.assert_called()

    def test_arc_drawn_for_nonzero_5g_clients(self):
        canvas = self._run({"CLIENTS2G": "0", "CLIENTS5G": "5"})
        canvas.create_arc.assert_called()

    def test_no_arc_when_both_clients_are_zero(self):
        canvas = self._run({"CLIENTS2G": "0", "CLIENTS5G": "0"})
        canvas.create_arc.assert_not_called()

    def test_no_arc_when_2g_clients_invalid(self):
        canvas = self._run({"CLIENTS2G": "bad", "CLIENTS5G": "0"})
        canvas.create_arc.assert_not_called()

    def test_no_arc_when_5g_clients_invalid(self):
        canvas = self._run({"CLIENTS2G": "0", "CLIENTS5G": "invalid"})
        canvas.create_arc.assert_not_called()

    def test_two_arcs_when_both_clients_nonzero(self):
        canvas = self._run({"CLIENTS2G": "3", "CLIENTS5G": "5"})
        self.assertEqual(canvas.create_arc.call_count, 2)

    # -- Bluetooth label --------------------------------------------------

    def test_bt_on_displayed_uppercase(self):
        self._run({"BT": "on"})
        label_calls_str = str(_tk_mock.Label.call_args_list)
        self.assertIn("ON", label_calls_str)

    def test_bt_off_displayed_uppercase(self):
        self._run({"BT": "off"})
        label_calls_str = str(_tk_mock.Label.call_args_list)
        self.assertIn("OFF", label_calls_str)

    def test_bt_unavailable_displayed_uppercase(self):
        self._run({"BT": "unavailable"})
        label_calls_str = str(_tk_mock.Label.call_args_list)
        self.assertIn("UNAVAILABLE", label_calls_str)

    # -- GPS label --------------------------------------------------------

    def test_gps_coordinates_displayed(self):
        self._run({"GPSLAT": "51.5074", "GPSLONG": "-0.1278"})
        label_calls_str = str(_tk_mock.Label.call_args_list)
        self.assertIn("51.5074", label_calls_str)
        self.assertIn("-0.1278", label_calls_str)

    def test_missing_gps_coords_show_placeholder(self):
        self._run({"GPSLAT": "", "GPSLONG": ""})
        label_calls_str = str(_tk_mock.Label.call_args_list)
        self.assertIn("--", label_calls_str)

    # -- battery labels ---------------------------------------------------

    def test_four_battery_labels_are_placed(self):
        mock_label = MagicMock()
        _tk_mock.Label.return_value = mock_label
        self._run()
        # 2 BT labels + 2 GPS labels + 4 battery labels = 8 .place() calls
        self.assertEqual(mock_label.place.call_count, 8)

    # -- refresh scheduling -----------------------------------------------

    def test_refresh_scheduled_after_3000ms(self):
        self._run()
        fancy_monitor.root.after.assert_called_with(
            3000, fancy_monitor.draw_dashboard
        )

    # -- ovals (donut background) -----------------------------------------

    def test_two_background_ovals_drawn(self):
        canvas = self._run()
        # One outer oval per band (2G + 5G) = at minimum 2; inner white
        # ovals add 2 more → at least 4 create_oval calls
        self.assertGreaterEqual(canvas.create_oval.call_count, 4)


# ===========================================================================
# Module-level constants
# ===========================================================================

class TestModuleConstants(unittest.TestCase):
    """Verify CSV_PATH and SCRIPT_DIR are set correctly."""

    def test_csv_path_points_to_tmp(self):
        self.assertEqual(fancy_monitor.CSV_PATH, "/tmp/display_data.csv")

    def test_script_dir_is_absolute(self):
        self.assertTrue(os.path.isabs(fancy_monitor.SCRIPT_DIR))

    def test_script_dir_is_a_directory(self):
        self.assertTrue(os.path.isdir(fancy_monitor.SCRIPT_DIR))

    def test_script_dir_contains_fancy_monitor(self):
        module_file = os.path.join(fancy_monitor.SCRIPT_DIR, "fancy_monitor.py")
        self.assertTrue(os.path.exists(module_file))


if __name__ == "__main__":
    unittest.main()
