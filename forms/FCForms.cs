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
                Application.Run(homeForm);
            });
            uiThread.SetApartmentState(ApartmentState.STA);
            uiThread.Start();
        }

        public enum Label
        {
            lAccount, lSync, lSyncInfo, lLocal, lLocalInfo,
        };

        public enum Button
        {
            bExit, bSync, bLocal,
        }


        public static void Test() => homeForm?.Invoke((MethodInvoker)homeForm.Test);

        public static void HomeT(Label label, string text)  =>
            homeForm?.Invoke((MethodInvoker)(() => homeForm.LabelText(label, text)));

        public static void HomeT(Button button, string text) =>
            homeForm?.Invoke((MethodInvoker)(() => homeForm.ButtonText(button, text)));

        public static void HomeBA(Button button, Action action) =>
            homeForm?.Invoke((MethodInvoker)(() => { homeForm.ButtonAction(button, (_, __) => action.Invoke()); }));

    }
}
