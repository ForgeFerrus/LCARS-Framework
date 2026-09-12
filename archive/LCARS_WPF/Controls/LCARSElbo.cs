using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;

namespace LCARSControls
{
    public class LCARSElbo : Control
    {
        public enum CornerType
        {
            TopLeft,
            TopRight,
            BottomLeft,
            BottomRight
        }

        public static readonly DependencyProperty CornerProperty =
            DependencyProperty.Register(nameof(Corner), typeof(CornerType), typeof(LCARSElbo),
                new PropertyMetadata(CornerType.TopLeft));

        public static readonly DependencyProperty BarThicknessProperty =
            DependencyProperty.Register(nameof(BarThickness), typeof(double), typeof(LCARSElbo),
                new PropertyMetadata(50.0));

        public static readonly DependencyProperty ColumnWidthProperty =
            DependencyProperty.Register(nameof(ColumnWidth), typeof(double), typeof(LCARSElbo),
                new PropertyMetadata(200.0));

        public static readonly DependencyProperty InnerArcRadiusProperty =
            DependencyProperty.Register(nameof(InnerArcRadius), typeof(double), typeof(LCARSElbo),
                new PropertyMetadata(30.0));

        public static readonly DependencyProperty FillColorProperty =
            DependencyProperty.Register(nameof(FillColor), typeof(Color), typeof(LCARSElbo),
                new PropertyMetadata(Colors.Orange));

        public static readonly DependencyProperty IsIlluminatedProperty =
            DependencyProperty.Register(nameof(IsIlluminated), typeof(bool), typeof(LCARSElbo),
                new PropertyMetadata(false, OnIsIlluminatedChanged));

        public CornerType Corner
        {
            get => (CornerType)GetValue(CornerProperty);
            set => SetValue(CornerProperty, value);
        }

        public double BarThickness
        {
            get => (double)GetValue(BarThicknessProperty);
            set => SetValue(BarThicknessProperty, value);
        }

        public double ColumnWidth
        {
            get => (double)GetValue(ColumnWidthProperty);
            set => SetValue(ColumnWidthProperty, value);
        }

        public double InnerArcRadius
        {
            get => (double)GetValue(InnerArcRadiusProperty);
            set => SetValue(InnerArcRadiusProperty, value);
        }

        public Color FillColor
        {
            get => (Color)GetValue(FillColorProperty);
            set => SetValue(FillColorProperty, value);
        }

        public bool IsIlluminated
        {
            get => (bool)GetValue(IsIlluminatedProperty);
            set => SetValue(IsIlluminatedProperty, value);
        }

        static LCARSElbo()
        {
            DefaultStyleKeyProperty.OverrideMetadata(typeof(LCARSElbo),
                new FrameworkPropertyMetadata(typeof(LCARSElbo)));
        }

        private static void OnIsIlluminatedChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is LCARSElbo elbo)
            {
                elbo.InvalidateVisual();
            }
        }

        protected override void OnRender(DrawingContext drawingContext)
        {
            base.OnRender(drawingContext);
            
            var rect = new Rect(0, 0, ActualWidth, ActualHeight);
            var currentColor = IsIlluminated ? FillColor : FillColor.Darken();
            
            DrawElboShape(drawingContext, rect, currentColor);
        }

        private void DrawElboShape(DrawingContext drawingContext, Rect rect, Color color)
        {
            var brush = new SolidColorBrush(color);
            var pen = new Pen(new SolidColorBrush(color.Darken()), 2);
            
            var path = new PathGeometry();
            var figure = new PathFigure();
            
            switch (Corner)
            {
                case CornerType.TopLeft:
                    DrawTopLeftElbo(figure, rect);
                    break;
                case CornerType.TopRight:
                    DrawTopRightElbo(figure, rect);
                    break;
                case CornerType.BottomLeft:
                    DrawBottomLeftElbo(figure, rect);
                    break;
                case CornerType.BottomRight:
                    DrawBottomRightElbo(figure, rect);
                    break;
            }
            
            path.Figures.Add(figure);
            drawingContext.DrawGeometry(brush, pen, path);
        }

        private void DrawTopLeftElbo(PathFigure figure, Rect rect)
        {
            // Horizontal bar
            figure.StartPoint = new Point(0, BarThickness / 2);
            figure.Segments.Add(new LineSegment(new Point(ColumnWidth, BarThickness / 2), false));
            figure.Segments.Add(new LineSegment(new Point(ColumnWidth, BarThickness), false));
            figure.Segments.Add(new LineSegment(new Point(BarThickness, BarThickness), false));
            
            // Corner arc
            var arcRect = new Rect(0, 0, InnerArcRadius * 2, InnerArcRadius * 2);
            figure.Segments.Add(new ArcSegment(new Point(BarThickness, InnerArcRadius), 
                new Size(InnerArcRadius, InnerArcRadius), 0, false, SweepDirection.Clockwise, false));
            
            // Vertical bar
            figure.Segments.Add(new LineSegment(new Point(BarThickness / 2, InnerArcRadius), false));
            figure.Segments.Add(new LineSegment(new Point(BarThickness / 2, rect.Height), false));
            figure.Segments.Add(new LineSegment(new Point(0, rect.Height), false));
            figure.Segments.Add(new LineSegment(new Point(0, BarThickness / 2), false));
        }

        private void DrawTopRightElbo(PathFigure figure, Rect rect)
        {
            // Horizontal bar
            figure.StartPoint = new Point(rect.Width - ColumnWidth, BarThickness / 2);
            figure.Segments.Add(new LineSegment(new Point(rect.Width - BarThickness, BarThickness / 2), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width - BarThickness, BarThickness), false));
            
            // Corner arc
            var arcRect = new Rect(rect.Width - InnerArcRadius * 2, 0, InnerArcRadius * 2, InnerArcRadius * 2);
            figure.Segments.Add(new ArcSegment(new Point(rect.Width - BarThickness, InnerArcRadius), 
                new Size(InnerArcRadius, InnerArcRadius), 0, false, SweepDirection.Clockwise, false));
            
            // Vertical bar
            figure.Segments.Add(new LineSegment(new Point(rect.Width - BarThickness / 2, InnerArcRadius), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width - BarThickness / 2, rect.Height), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width, rect.Height), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width, BarThickness / 2), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width - ColumnWidth, BarThickness / 2), false));
        }

        private void DrawBottomLeftElbo(PathFigure figure, Rect rect)
        {
            // Horizontal bar
            figure.StartPoint = new Point(0, rect.Height - BarThickness / 2);
            figure.Segments.Add(new LineSegment(new Point(ColumnWidth, rect.Height - BarThickness / 2), false));
            figure.Segments.Add(new LineSegment(new Point(ColumnWidth, rect.Height - BarThickness), false));
            figure.Segments.Add(new LineSegment(new Point(BarThickness, rect.Height - BarThickness), false));
            
            // Corner arc
            var arcRect = new Rect(0, rect.Height - InnerArcRadius * 2, InnerArcRadius * 2, InnerArcRadius * 2);
            figure.Segments.Add(new ArcSegment(new Point(BarThickness, rect.Height - InnerArcRadius), 
                new Size(InnerArcRadius, InnerArcRadius), 0, false, SweepDirection.Clockwise, false));
            
            // Vertical bar
            figure.Segments.Add(new LineSegment(new Point(BarThickness / 2, rect.Height - InnerArcRadius), false));
            figure.Segments.Add(new LineSegment(new Point(BarThickness / 2, 0), false));
            figure.Segments.Add(new LineSegment(new Point(0, 0), false));
            figure.Segments.Add(new LineSegment(new Point(0, rect.Height - BarThickness / 2), false));
        }

        private void DrawBottomRightElbo(PathFigure figure, Rect rect)
        {
            // Horizontal bar
            figure.StartPoint = new Point(rect.Width - ColumnWidth, rect.Height - BarThickness / 2);
            figure.Segments.Add(new LineSegment(new Point(rect.Width - BarThickness, rect.Height - BarThickness / 2), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width - BarThickness, rect.Height - BarThickness), false));
            
            // Corner arc
            var arcRect = new Rect(rect.Width - InnerArcRadius * 2, rect.Height - InnerArcRadius * 2, InnerArcRadius * 2, InnerArcRadius * 2);
            figure.Segments.Add(new ArcSegment(new Point(rect.Width - BarThickness, rect.Height - InnerArcRadius), 
                new Size(InnerArcRadius, InnerArcRadius), 0, false, SweepDirection.Clockwise, false));
            
            // Vertical bar
            figure.Segments.Add(new LineSegment(new Point(rect.Width - BarThickness / 2, rect.Height - InnerArcRadius), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width - BarThickness / 2, 0), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width, 0), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width, rect.Height - BarThickness / 2), false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width - ColumnWidth, rect.Height - BarThickness / 2), false));
        }
    }
}
