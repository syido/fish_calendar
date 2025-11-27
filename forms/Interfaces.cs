using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FCForms
{
    internal interface Visible
    {
        public void ButtonText(FCForms.Button button, string text);
        public void ButtonAction(FCForms.Button button, Action<object, EventArgs> action);
        public void LabelText(FCForms.Label label, string text);
    }
}
