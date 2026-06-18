# Helps close out tkinter error dialog for tests
import unittest
from unittest.mock import patch


class UIErrorGuardTestCase(unittest.TestCase):
    # Non-error dialogs only need a safe, non-blocking return value.
    _AUTO_DISMISS = {
        'showinfo': 'ok',
        'showwarning': 'ok',
        'askquestion': 'no',
        'askyesno': False,
        'askokcancel': False,
        'askretrycancel': False,
    }

    def setUp(self):
        super().setUp()
        self._ui_errors = []

        def _record_error(*args, **kwargs):
            # messagebox.showerror(title, message): capture for the failure msg
            self._ui_errors.append(args[:2] if args else kwargs)
            return 'ok'

        patchers = [patch('tkinter.messagebox.showerror', side_effect=_record_error)]
        for name, retval in self._AUTO_DISMISS.items():
            patchers.append(patch(f'tkinter.messagebox.{name}', return_value=retval))
        # File choosers return "" (i.e. the user cancelled) so nothing blocks.
        for name in ('askopenfilename', 'asksaveasfilename', 'askdirectory'):
            patchers.append(patch(f'tkinter.filedialog.{name}', return_value=''))

        for p in patchers:
            p.start()
            self.addCleanup(p.stop)

    def tearDown(self):
        super().tearDown()
        if self._ui_errors:
            self.fail(f"UI error dialog(s) shown during test: {self._ui_errors}")
