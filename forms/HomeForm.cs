using System;
using System.Windows.Forms;

namespace FCForms
{
    public partial class HomeForm : Form, Visible
    {
        public HomeForm()
        {
            InitializeComponent();
        }

        public void Test() { }


        Label GetLabel(FCForms.Label label)
        {
            return label switch
            {
                FCForms.Label.lLocal => lLocal,
                FCForms.Label.lAccount => lAccount,
                FCForms.Label.lLocalInfo => lLocalInfo,
                FCForms.Label.lSync => lSync,
                FCForms.Label.lSyncInfo => lSyncInfo,
                _ => null
            };
        }

        Button GetButton(FCForms.Button button)
        {
            return button switch
            {
                FCForms.Button.bLocal => bLocal,
                FCForms.Button.bSync => bSync,
                FCForms.Button.bExit => bExit,
                _ => null
            };
        }



        public void LabelText(FCForms.Label label, string text)
        {
            var l = GetLabel(label);
            l?.Text = text;
        }

        public void ButtonText(FCForms.Button button, string text)
        {
            var b = GetButton(button);
            b?.Text = text;
        }

        
        public void ButtonAction(FCForms.Button button, Action<object, EventArgs> action)
        {
            var b = GetButton(button);
            b?.Click += new EventHandler(action);
        }

        protected override void SetVisibleCore(bool value)
        {
            if (!IsHandleCreated)
                value = false;
            base.SetVisibleCore(value);
        }

    }
}
