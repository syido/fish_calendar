using System;
using System.Windows.Forms;

namespace FCForms
{
    public partial class HomeForm : Form
    {
        public HomeForm()
        {
            InitializeComponent();
        }

        public void Test() { }


        Label GetLabel(FCForms.Label label)
        {
            Label l = null;
            switch (label)
            {
                case FCForms.Label.lLocal: l = lLocal; break;
                case FCForms.Label.lAccount: l = lAccount; break;
                case FCForms.Label.lLocalInfo: l = lLocalInfo; break;
                case FCForms.Label.lSyncInfo: l = lSyncInfo; break;
                case FCForms.Label.lSync: l = lSync; break;
            }
            return l;
        }

        Button GetButton(FCForms.Button button)
        {
            Button b = null;
            switch (button)
            {
                case FCForms.Button.bLocal: b = bLocal; break;
                case FCForms.Button.bSync: b = bSync; break;
                case FCForms.Button.bExit: b = bExit; break;
            }
            return b;
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
    }
}
