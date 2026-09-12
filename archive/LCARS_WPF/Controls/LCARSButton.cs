using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Input;

namespace LCARSControls
{
    public class LCARSButton : Button
    {
        public enum IlluminationState
        {
            Off,
            On,
            Flashing
        }

        public enum StumpPosition
        {
            None,
            Left,
            Right,
            Both
        }

        // Dependency Properties
        public static readonly DependencyProperty IlluminationProperty =
            DependencyProperty.Register(nameof(Illumination), typeof(IlluminationState), typeof(LCARSButton),
                new PropertyMetadata(IlluminationState.Off, OnIlluminationChanged));

        public static readonly DependencyProperty StumpsProperty =
            DependencyProperty.Register(nameof(Stumps), typeof(StumpPosition), typeof(LCARSButton),
                new PropertyMetadata(StumpPosition.None, OnStumpsChanged));

        public static readonly DependencyProperty OnColorProperty =
            DependencyProperty.Register(nameof(OnColor), typeof(Color), typeof(LCARSButton),
                new PropertyMetadata(Colors.Orange));

        public static readonly DependencyProperty OffColorProperty =
            DependencyProperty.Register(nameof(OffColor), typeof(Color), typeof(LCARSButton),
                new PropertyMetadata(Color.FromRgb(102, 102, 0)));

        public static readonly DependencyProperty FlashColorProperty =
            DependencyProperty.Register(nameof(FlashColor), typeof(Color), typeof(LCARSButton),
                new PropertyMetadata(Colors.Yellow));

        private bool _isLit = false;
        private Storyboard _flashStoryboard;
        private DoubleAnimation _flashAnimation;

        public IlluminationState Illumination
        {
            get => (IlluminationState)GetValue(IlluminationProperty);
            set => SetValue(IlluminationProperty, value);
        }

        public StumpPosition Stumps
        {
            get => (StumpPosition)GetValue(StumpsProperty);
            set => SetValue(StumpsProperty, value);
        }

        public Color OnColor
        {
            get => (Color)GetValue(OnColorProperty);
            set => SetValue(OnColorProperty, value);
        }

        public Color OffColor
        {
            get => (Color)GetValue(OffColorProperty);
            set => SetValue(OffColorProperty, value);
        }

        public Color FlashColor
        {
            get => (Color)GetValue(FlashColorProperty);
            set => SetValue(FlashColorProperty, value);
        }

        static LCARSButton()
        {
            DefaultStyleKeyProperty.OverrideMetadata(typeof(LCARSButton),
                new FrameworkPropertyMetadata(typeof(LCARSButton)));
        }

        public LCARSButton()
        {
            InitializeFlashAnimation();
            Click += (s, e) => PlayClickSound();
        }

        private void InitializeFlashAnimation()
        {
            _flashStoryboard = new Storyboard();
            _flashAnimation = new DoubleAnimation
            {
                Duration = TimeSpan.FromMilliseconds(500),
                AutoReverse = true,
                RepeatBehavior = RepeatBehavior.Forever
            };
            _flashStoryboard.Children.Add(_flashAnimation);
        }

        private static void OnIlluminationChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is LCARSButton button)
            {
                button.UpdateIllumination();
            }
        }

        private static void OnStumpsChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is LCARSButton button)
            {
                button.InvalidateVisual();
            }
        }

        private void UpdateIllumination()
        {
            switch (Illumination)
            {
                case IlluminationState.On:
                    _isLit = true;
                    StopFlashing();
                    break;
                case IlluminationState.Off:
                    _isLit = false;
                    StopFlashing();
                    break;
                case IlluminationState.Flashing:
                    StartFlashing();
                    break;
            }
            InvalidateVisual();
        }

        private void StartFlashing()
        {
            _flashAnimation.From = 0;
            _flashAnimation.To = 1;
            Storyboard.SetTarget(_flashAnimation, this);
            Storyboard.SetTargetProperty(_flashAnimation, new PropertyPath("FlashOpacity"));
            _flashStoryboard.Begin();
        }

        private void StopFlashing()
        {
            _flashStoryboard.Stop();
        }

        private double FlashOpacity
        {
            get => _isLit ? 1.0 : 0.0;
            set
            {
                _isLit = value > 0.5;
                InvalidateVisual();
            }
        }

        private void PlayClickSound()
        {
            // TODO: Implement sound playback
            System.Media.SystemSounds.Beep.Play();
        }

        public override void OnApplyTemplate()
        {
            base.OnApplyTemplate();
            UpdateIllumination();
        }

        protected override void OnRender(DrawingContext drawingContext)
        {
            base.OnRender(drawingContext);
            
            var rect = new Rect(0, 0, ActualWidth, ActualHeight);
            var currentColor = GetCurrentColor();
            
            // Draw main button shape
            DrawButtonShape(drawingContext, rect, currentColor);
            
            // Draw stumps if needed
            if (Stumps != StumpPosition.None)
            {
                DrawStumps(drawingContext, rect, currentColor);
            }
            
            // Draw text
            DrawText(drawingContext, rect);
        }

        private Color GetCurrentColor()
        {
            if (Illumination == IlluminationState.Flashing && _isLit)
                return FlashColor;
            return _isLit ? OnColor : OffColor;
        }

        private void DrawButtonShape(DrawingContext drawingContext, Rect rect, Color color)
        {
            var brush = new SolidColorBrush(color);
            var pen = new Pen(new SolidColorBrush(color.Darken()), 2);
            
            // Draw rounded rectangle
            var radius = 8;
            var path = new PathGeometry();
            var figure = new PathFigure();
            
            figure.StartPoint = new Point(radius, 0);
            figure.Segments.Add(new LineSegment(new Point(rect.Width - radius, 0), false));
            figure.Segments.Add(new ArcSegment(new Point(rect.Width, radius), 
                new Size(radius, radius), 0, false, SweepDirection.Clockwise, false));
            figure.Segments.Add(new LineSegment(new Point(rect.Width, rect.Height - radius), false));
            figure.Segments.Add(new ArcSegment(new Point(rect.Width - radius, rect.Height), 
                new Size(radius, radius), 0, false, SweepDirection.Clockwise, false));
            figure.Segments.Add(new LineSegment(new Point(radius, rect.Height), false));
            figure.Segments.Add(new ArcSegment(new Point(0, rect.Height - radius), 
                new Size(radius, radius), 0, false, SweepDirection.Clockwise, false));
            figure.Segments.Add(new LineSegment(new Point(0, radius), false));
            figure.Segments.Add(new ArcSegment(new Point(radius, 0), 
                new Size(radius, radius), 0, false, SweepDirection.Clockwise, false));
            
            path.Figures.Add(figure);
            drawingContext.DrawGeometry(brush, pen, path);
        }

        private void DrawStumps(DrawingContext drawingContext, Rect rect, Color color)
        {
            var brush = new SolidColorBrush(color);
            var pen = new Pen(new SolidColorBrush(color.Darken()), 2);
            var stumpWidth = 20;
            var stumpHeight = rect.Height / 2;
            
            if (Stumps == StumpPosition.Left || Stumps == StumpPosition.Both)
            {
                var leftStump = new Rect(-stumpWidth, rect.Height / 2 - stumpHeight / 2, 
                    stumpWidth, stumpHeight);
                var leftEllipse = new EllipseGeometry(leftStump);
                drawingContext.DrawGeometry(brush, pen, leftEllipse);
            }
            
            if (Stumps == StumpPosition.Right || Stumps == StumpPosition.Both)
            {
                var rightStump = new Rect(rect.Width, rect.Height / 2 - stumpHeight / 2, 
                    stumpWidth, stumpHeight);
                var rightEllipse = new EllipseGeometry(rightStump);
                drawingContext.DrawGeometry(brush, pen, rightEllipse);
            }
        }

        private void DrawText(DrawingContext drawingContext, Rect rect)
        {
            var typeface = new Typeface(new FontFamily("Arial"), FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
            var formattedText = new FormattedText(Content.ToString(), 
                System.Globalization.CultureInfo.CurrentCulture, 
                FlowDirection.LeftToRight, 
                typeface, 
                14, 
                Brushes.Black,
                new NumberSubstitution(), 
                TextFormattingMode.Display, 
                96);
            
            var textPoint = new Point(0, rect.Height / 2 - formattedText.Height / 2);
            drawingContext.DrawText(formattedText, textPoint);
        }
    }

    public static class ColorExtensions
    {
        public static Color Darken(this Color color)
        {
            return Color.FromRgb(
                (byte)(color.R * 0.7),
                (byte)(color.G * 0.7),
                (byte)(color.B * 0.7));
        }
    }
}
