// LCARS Elbow - Компонент для створення elbows з плавними дугами
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(SpriteRenderer))]
public class LCARSElbow : MonoBehaviour
{
    [Header("Параметри Elbow")]
    public CornerType cornerType = CornerType.TopLeft;
    public float thickness = 1f;
    public Color elbowColor = Color.yellow;
    
    [Header("Текст")]
    public string elbowText = "◤ LCARS";
    public int fontSize = 24;
    
    private SpriteRenderer spriteRenderer;
    private GameObject textObject;
    private TextMeshPro textMesh;
    
    void Start()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        CreateElbowSprite();
        CreateText();
    }
    
    void CreateElbowSprite()
    {
        // Створюємо текстуру для elbow
        int textureSize = 256;
        Texture2D texture = new Texture2D(textureSize, textureSize);
        
        // Очищуємо текстуру
        Color[] pixels = new Color[textureSize * textureSize];
        for (int i = 0; i < pixels.Length; i++)
        {
            pixels[i] = Color.clear;
        }
        
        // Малюємо elbow з плавною дугою
        DrawSmoothElbow(texture, pixels, textureSize);
        
        texture.SetPixels(pixels);
        texture.Apply();
        
        // Створюємо спрайт
        Sprite sprite = Sprite.Create(texture, new Rect(0, 0, textureSize, textureSize), new Vector2(0.5f, 0.5f));
        spriteRenderer.sprite = sprite;
        spriteRenderer.color = elbowColor;
        
        // Налаштування фільтрації для плавності
        texture.filterMode = FilterMode.Bilinear;
    }
    
    void DrawSmoothElbow(Texture2D texture, Color[] pixels, int size)
    {
        float center = size / 2f;
        float radius = size / 4f;
        
        // Малюємо залежно від типу кута
        switch (cornerType)
        {
            case CornerType.TopLeft:
                DrawTopLeftElbow(pixels, size, center, radius);
                break;
            case CornerType.TopRight:
                DrawTopRightElbow(pixels, size, center, radius);
                break;
            case CornerType.BottomLeft:
                DrawBottomLeftElbow(pixels, size, center, radius);
                break;
            case CornerType.BottomRight:
                DrawBottomRightElbow(pixels, size, center, radius);
                break;
        }
    }
    
    void DrawTopLeftElbow(Color[] pixels, int size, float center, float radius)
    {
        int thicknessPixels = (int)(size * thickness / 4f);
        
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                int index = y * size + x;
                
                // Горизонтальна частина
                if (y >= center - thicknessPixels/2 && y <= center + thicknessPixels/2 && x >= center)
                {
                    pixels[index] = Color.white;
                }
                
                // Вертикальна частина
                if (x >= center - thicknessPixels/2 && x <= center + thicknessPixels/2 && y <= center)
                {
                    pixels[index] = Color.white;
                }
                
                // Дуга - плавна
                float dx = x - center;
                float dy = y - center;
                float distance = Mathf.Sqrt(dx * dx + dy * dy);
                
                if (distance <= radius && distance >= radius - thicknessPixels/2)
                {
                    // Перевіряємо чи точка в куті
                    if (x <= center && y <= center)
                    {
                        // Плавний градієнт по краю дуги
                        float edgeFactor = 1f - Mathf.Abs(distance - (radius - thicknessPixels/2)) / (thicknessPixels/2f);
                        pixels[index] = Color.Lerp(Color.clear, Color.white, edgeFactor);
                    }
                }
            }
        }
    }
    
    void DrawTopRightElbow(Color[] pixels, int size, float center, float radius)
    {
        int thicknessPixels = (int)(size * thickness / 4f);
        
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                int index = y * size + x;
                
                // Горизонтальна частина
                if (y >= center - thicknessPixels/2 && y <= center + thicknessPixels/2 && x <= center)
                {
                    pixels[index] = Color.white;
                }
                
                // Вертикальна частина
                if (x >= center - thicknessPixels/2 && x <= center + thicknessPixels/2 && y <= center)
                {
                    pixels[index] = Color.white;
                }
                
                // Дуга
                float dx = x - center;
                float dy = y - center;
                float distance = Mathf.Sqrt(dx * dx + dy * dy);
                
                if (distance <= radius && distance >= radius - thicknessPixels/2)
                {
                    if (x >= center && y <= center)
                    {
                        float edgeFactor = 1f - Mathf.Abs(distance - (radius - thicknessPixels/2)) / (thicknessPixels/2f);
                        pixels[index] = Color.Lerp(Color.clear, Color.white, edgeFactor);
                    }
                }
            }
        }
    }
    
    void DrawBottomLeftElbow(Color[] pixels, int size, float center, float radius)
    {
        int thicknessPixels = (int)(size * thickness / 4f);
        
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                int index = y * size + x;
                
                // Горизонтальна частина
                if (y >= center - thicknessPixels/2 && y <= center + thicknessPixels/2 && x >= center)
                {
                    pixels[index] = Color.white;
                }
                
                // Вертикальна частина
                if (x >= center - thicknessPixels/2 && x <= center + thicknessPixels/2 && y >= center)
                {
                    pixels[index] = Color.white;
                }
                
                // Дуга
                float dx = x - center;
                float dy = y - center;
                float distance = Mathf.Sqrt(dx * dx + dy * dy);
                
                if (distance <= radius && distance >= radius - thicknessPixels/2)
                {
                    if (x <= center && y >= center)
                    {
                        float edgeFactor = 1f - Mathf.Abs(distance - (radius - thicknessPixels/2)) / (thicknessPixels/2f);
                        pixels[index] = Color.Lerp(Color.clear, Color.white, edgeFactor);
                    }
                }
            }
        }
    }
    
    void DrawBottomRightElbow(Color[] pixels, int size, float center, float radius)
    {
        int thicknessPixels = (int)(size * thickness / 4f);
        
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                int index = y * size + x;
                
                // Горизонтальна частина
                if (y >= center - thicknessPixels/2 && y <= center + thicknessPixels/2 && x <= center)
                {
                    pixels[index] = Color.white;
                }
                
                // Вертикальна частина
                if (x >= center - thicknessPixels/2 && x <= center + thicknessPixels/2 && y >= center)
                {
                    pixels[index] = Color.white;
                }
                
                // Дуга
                float dx = x - center;
                float dy = y - center;
                float distance = Mathf.Sqrt(dx * dx + dy * dy);
                
                if (distance <= radius && distance >= radius - thicknessPixels/2)
                {
                    if (x >= center && y >= center)
                    {
                        float edgeFactor = 1f - Mathf.Abs(distance - (radius - thicknessPixels/2)) / (thicknessPixels/2f);
                        pixels[index] = Color.Lerp(Color.clear, Color.white, edgeFactor);
                    }
                }
            }
        }
    }
    
    void CreateText()
    {
        if (string.IsNullOrEmpty(elbowText))
            return;
            
        textObject = new GameObject("ElbowText");
        textObject.transform.SetParent(transform);
        textObject.transform.localPosition = new Vector3(-0.3f, 0f, -0.1f);
        
        textMesh = textObject.AddComponent<TextMeshPro>();
        textMesh.text = elbowText;
        textMesh.fontSize = fontSize;
        textMesh.color = Color.black;
        textMesh.alignment = TextAlignmentOptions.Left;
        textMesh.fontStyle = FontStyles.Bold;
        
        // Додаємо контур для кращої читабельності
        textMesh.outlineColor = Color.white;
        textMesh.outlineWidth = 0.1f;
    }
    
    public void UpdateElbowColor(Color newColor)
    {
        elbowColor = newColor;
        spriteRenderer.color = elbowColor;
    }
    
    public void UpdateText(string newText)
    {
        elbowText = newText;
        if (textMesh != null)
        {
            textMesh.text = newText;
        }
    }
}

public enum CornerType
{
    TopLeft,
    TopRight,
    BottomLeft,
    BottomRight
}
