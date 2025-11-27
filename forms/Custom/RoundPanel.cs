using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace Custom
{
    public class RoundPanel : Panel
    {
        public int Radius { get; set; } = 10;
        public int BorderThickness { get; set; } = 1;
        public Color BorderColor { get; set; } = Color.Gray;

        public RoundPanel()
        {
            this.DoubleBuffered = true;
            this.ResizeRedraw = true;
            this.SetStyle(ControlStyles.OptimizedDoubleBuffer, true);
        }

        protected override void OnResize(System.EventArgs e)
        {
            base.OnResize(e);
            Invalidate();
        }

        protected override void OnSizeChanged(System.EventArgs e)
        {
            base.OnSizeChanged(e);
            UpdateRegion();
        }

        private void UpdateRegion()
        {
            int r = Radius;
            Rectangle rect = new Rectangle(0, 0, Width, Height);

            using (GraphicsPath path = CreatePath(rect, r))
            {
                this.Region = new Region(path);
            }
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);

            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
            e.Graphics.PixelOffsetMode = PixelOffsetMode.HighQuality;
            e.Graphics.CompositingQuality = CompositingQuality.HighQuality;

            Rectangle rect = new Rectangle(
                BorderThickness / 2,
                BorderThickness / 2,
                Width - BorderThickness,
                Height - BorderThickness
            );

            using (GraphicsPath path = CreatePath(rect, Radius))
            using (Pen pen = new Pen(BorderColor, BorderThickness))
            {
                e.Graphics.DrawPath(pen, path);
            }
        }

        private GraphicsPath CreatePath(Rectangle rect, int r)
        {
            GraphicsPath path = new GraphicsPath();
            int d = r * 2;

            path.AddArc(rect.X, rect.Y, d, d, 180, 90);
            path.AddArc(rect.Right - d, rect.Y, d, d, 270, 90);
            path.AddArc(rect.Right - d, rect.Bottom - d, d, d, 0, 90);
            path.AddArc(rect.X, rect.Bottom - d, d, d, 90, 90);

            path.CloseFigure();
            return path;
        }
    }
}
