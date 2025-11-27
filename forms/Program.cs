#if DEBUG
using System;

namespace FCForms
{
    internal static class Program
    {
        [STAThread]
        static void Main()
        {

            FCForms.Run();
            FCForms.ReadyThen(() => 
            {
                FCForms.HomeT(FCForms.Label.lAccount, "aaaaa");
            });
            
        }
    }
}
#endif