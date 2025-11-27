using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;


namespace FCForms
{
    public static class FCForms
    {
        private static Thread uiThread = null;
        private static HomeForm homeForm = null;

        private static event Action ready;

        [DllImport("user32.dll")]
        private static extern bool SetProcessDpiAwarenessContext(int dpiFlag);

        public static void Run()
        {
            if (uiThread != null) return;

            uiThread = new Thread(() =>
            {
                SetProcessDpiAwarenessContext(-4);
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);

                homeForm = new HomeForm();
                homeForm.Load += (_, __) => { ready?.Invoke(); };
                Application.Run(homeForm);
            });
            uiThread.SetApartmentState(ApartmentState.STA);
            uiThread.Start();
        }


        public static void Test() => homeForm?.Invoke((MethodInvoker)homeForm.Test);

        public static void Hide(Forms form) => GetForm(form)?.Hide();
        public static void Show(Forms forms) => GetForm(forms)?.Show();

        public static void LabelText(Forms form, Label label, string text) =>
            GetForm(form).Invoke((MethodInvoker)(() => (GetForm(form) as Visible).LabelText(label, text)));

        public static void ButtonText(Forms form, Button button, string text) =>
            GetForm(form).Invoke((MethodInvoker)(() => (GetForm(form) as Visible).ButtonText(button, text)));

        public static void _ButtonAssign(Forms form, Button button, Action action) =>
            GetForm(form).Invoke((MethodInvoker)(() => { (GetForm(form) as Visible).ButtonAction(button, (_, __) => action.Invoke()); }));

        public static void _ReadyThen(Action action) => ready += action;


        public enum Label
        {
            lAccount, lSync, lSyncInfo, lLocal, lLocalInfo,
        };

        public enum Button
        {
            bExit, bSync, bLocal,
        }

        public enum Forms
        {
            Home,
        }

        private static Form GetForm(Forms form)
        {
            return form switch
            {
                Forms.Home => homeForm,
                _ => null
            };
        }
    }
}
