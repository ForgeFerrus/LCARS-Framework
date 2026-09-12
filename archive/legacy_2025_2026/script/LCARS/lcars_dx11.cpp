// LCARS DirectX 11 - Справжній LCARS з C++
#include <windows.h>
#include <d3d11.h>
#include <d3dcompiler.h>
#include <DirectXMath.h>
#include <vector>
#include <string>

#pragma comment(lib, "d3d11.lib")
#pragma comment(lib, "d3dcompiler.lib")

using namespace DirectX;

// LCARS палітра
struct LCARSPalette {
    XMFLOAT3 elbows[8];
    XMFLOAT3 buttons[8];
    XMFLOAT3 displays[8];
    XMFLOAT3 scanners[8];
    
    LCARSPalette() {
        // Жовті elbows
        elbows[0] = XMFLOAT3(1.0f, 1.0f, 0.0f);
        elbows[1] = XMFLOAT3(1.0f, 0.8f, 0.0f);
        
        // Помаранчеві кнопки
        buttons[0] = XMFLOAT3(1.0f, 0.6f, 0.0f);
        buttons[1] = XMFLOAT3(0.0f, 1.0f, 0.0f);
        buttons[2] = XMFLOAT3(0.2f, 0.4f, 0.8f);
        buttons[3] = XMFLOAT3(1.0f, 0.0f, 0.0f);
        
        // Сині дисплеї
        displays[0] = XMFLOAT3(0.1f, 0.3f, 0.6f);
        displays[1] = XMFLOAT3(0.2f, 0.4f, 0.8f);
        
        // Зелені сканери
        scanners[0] = XMFLOAT3(0.0f, 1.0f, 0.0f);
        scanners[1] = XMFLOAT3(0.0f, 0.8f, 0.0f);
    }
};

// Вершина для LCARS
struct LCARSVertex {
    XMFLOAT3 position;
    XMFLOAT3 color;
    float animPhase;
};

// LCARS елемент
struct LCARSElement {
    XMFLOAT2 position;
    XMFLOAT2 size;
    XMFLOAT3 color;
    std::string type;
    float animPhase;
};

class LCARSDX11 {
private:
    HWND hWnd;
    D3D11_DEVICE* device;
    D3D11_DEVICE_CONTEXT* context;
    IDXGISwapChain* swapChain;
    ID3D11RenderTargetView* renderTargetView;
    ID3D11VertexShader* vertexShader;
    ID3D11PixelShader* pixelShader;
    ID3D11InputLayout* inputLayout;
    ID3D11Buffer* vertexBuffer;
    ID3D11Buffer* constantBuffer;
    
    LCARSPalette palette;
    std::vector<LCARSElement> elements;
    float time;
    
public:
    LCARSDX11() : device(nullptr), context(nullptr), swapChain(nullptr),
                  renderTargetView(nullptr), vertexShader(nullptr),
                  pixelShader(nullptr), inputLayout(nullptr),
                  vertexBuffer(nullptr), constantBuffer(nullptr),
                  time(0.0f) {}
                  
    ~LCARSDX11() {
        Cleanup();
    }
    
    bool Initialize() {
        // Створюємо вікно
        if (!CreateWindow()) return false;
        
        // Ініціалізуємо DirectX 11
        if (!InitDirectX11()) return false;
        
        // Створюємо шейдери
        if (!CreateShaders()) return false;
        
        // Створюємо буфери
        if (!CreateBuffers()) return false;
        
        // Ініціалізуємо LCARS елементи
        InitLCARSElements();
        
        return true;
    }
    
    bool CreateWindow() {
        WNDCLASSEX wc = {};
        wc.cbSize = sizeof(WNDCLASSEX);
        wc.style = CS_HREDRAW | CS_VREDRAW;
        wc.lpfnWndProc = WndProc;
        wc.hInstance = GetModuleHandle(nullptr);
        wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
        wc.hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH);
        wc.lpszClassName = L"LCARSDX11";
        
        RegisterClassEx(&wc);
        
        // Повноекранне вікно
        hWnd = CreateWindowEx(
            WS_EX_TOPMOST,
            L"LCARSDX11",
            L"LCARS DirectX 11",
            WS_POPUP,
            0, 0,
            GetSystemMetrics(SM_CXSCREEN),
            GetSystemMetrics(SM_CYSCREEN),
            nullptr, nullptr, GetModuleHandle(nullptr), nullptr
        );
        
        return hWnd != nullptr;
    }
    
    bool InitDirectX11() {
        DXGI_SWAP_CHAIN_DESC scd = {};
        scd.BufferCount = 1;
        scd.BufferDesc.Width = GetSystemMetrics(SM_CXSCREEN);
        scd.BufferDesc.Height = GetSystemMetrics(SM_CYSCREEN);
        scd.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
        scd.BufferDesc.RefreshRate.Numerator = 60;
        scd.BufferDesc.RefreshRate.Denominator = 1;
        scd.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
        scd.OutputWindow = hWnd;
        scd.SampleDesc.Count = 1;
        scd.SampleDesc.Quality = 0;
        scd.Windowed = FALSE;
        scd.SwapEffect = DXGI_SWAP_EFFECT_DISCARD;
        
        D3D_FEATURE_LEVEL featureLevels[] = { D3D_FEATURE_LEVEL_11_0 };
        
        HRESULT hr = D3D11CreateDeviceAndSwapChain(
            nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, 0,
            featureLevels, 1, D3D11_SDK_VERSION,
            &scd, &swapChain, &device, nullptr, &context
        );
        
        if (FAILED(hr)) return false;
        
        // Створюємо render target
        ID3D11Texture2D* backBuffer;
        hr = swapChain->GetBuffer(0, __uuidof(ID3D11Texture2D), (void**)&backBuffer);
        if (FAILED(hr)) return false;
        
        hr = device->CreateRenderTargetView(backBuffer, nullptr, &renderTargetView);
        backBuffer->Release();
        if (FAILED(hr)) return false;
        
        context->OMSetRenderTargets(1, &renderTargetView, nullptr);
        
        // Налаштування viewport
        D3D11_VIEWPORT vp = {};
        vp.Width = (float)GetSystemMetrics(SM_CXSCREEN);
        vp.Height = (float)GetSystemMetrics(SM_CYSCREEN);
        vp.MinDepth = 0.0f;
        vp.MaxDepth = 1.0f;
        vp.TopLeftX = 0.0f;
        vp.TopLeftY = 0.0f;
        context->RSSetViewports(1, &vp);
        
        return true;
    }
    
    bool CreateShaders() {
        // Vertex shader
        const char* vsSource = R"(
            cbuffer ConstantBuffer : register(b0)
            {
                matrix WorldViewProj;
                float Time;
            }
            
            struct VS_INPUT {
                float3 Pos : POSITION;
                float3 Color : COLOR;
                float AnimPhase : TEXCOORD0;
            };
            
            struct PS_INPUT {
                float4 Pos : SV_POSITION;
                float3 Color : COLOR;
            };
            
            PS_INPUT VS(VS_INPUT input) {
                PS_INPUT output = (PS_INPUT)0;
                
                // Пульсація кнопок
                float pulse = sin(Time * 2.0 + input.AnimPhase) * 0.02;
                float3 pos = input.Pos * (1.0 + pulse);
                
                output.Pos = mul(float4(pos, 1.0f), WorldViewProj);
                output.Color = input.Color;
                
                return output;
            }
        )";
        
        ID3DBlob* vsBlob = nullptr;
        HRESULT hr = D3DCompile(vsSource, strlen(vsSource), nullptr, nullptr, nullptr, "VS", "vs_4_0", 0, 0, &vsBlob, nullptr);
        if (FAILED(hr)) return false;
        
        hr = device->CreateVertexShader(vsBlob->GetBufferPointer(), vsBlob->GetBufferSize(), nullptr, &vertexShader);
        if (FAILED(hr)) {
            vsBlob->Release();
            return false;
        }
        
        // Pixel shader
        const char* psSource = R"(
            struct PS_INPUT {
                float4 Pos : SV_POSITION;
                float3 Color : COLOR;
            };
            
            float4 PS(PS_INPUT input) : SV_Target {
                return float4(input.Color, 1.0f);
            }
        )";
        
        ID3DBlob* psBlob = nullptr;
        hr = D3DCompile(psSource, strlen(psSource), nullptr, nullptr, nullptr, "PS", "ps_4_0", 0, 0, &psBlob, nullptr);
        if (FAILED(hr)) {
            vsBlob->Release();
            return false;
        }
        
        hr = device->CreatePixelShader(psBlob->GetBufferPointer(), psBlob->GetBufferSize(), nullptr, &pixelShader);
        psBlob->Release();
        if (FAILED(hr)) {
            vsBlob->Release();
            return false;
        }
        
        // Input layout
        D3D11_INPUT_ELEMENT_DESC layout[] = {
            { "POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D11_INPUT_PER_VERTEX_DATA, 0 },
            { "COLOR", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 12, D3D11_INPUT_PER_VERTEX_DATA, 0 },
            { "TEXCOORD", 0, DXGI_FORMAT_R32_FLOAT, 0, 24, D3D11_INPUT_PER_VERTEX_DATA, 0 }
        };
        
        hr = device->CreateInputLayout(layout, 3, vsBlob->GetBufferPointer(), vsBlob->GetBufferSize(), &inputLayout);
        vsBlob->Release();
        if (FAILED(hr)) return false;
        
        return true;
    }
    
    bool CreateBuffers() {
        // Vertex buffer
        D3D11_BUFFER_DESC bd = {};
        bd.Usage = D3D11_USAGE_DYNAMIC;
        bd.ByteWidth = sizeof(LCARSVertex) * 10000;
        bd.BindFlags = D3D11_BIND_VERTEX_BUFFER;
        bd.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;
        
        HRESULT hr = device->CreateBuffer(&bd, nullptr, &vertexBuffer);
        if (FAILED(hr)) return false;
        
        // Constant buffer
        bd.Usage = D3D11_USAGE_DYNAMIC;
        bd.ByteWidth = sizeof(XMMATRIX) + sizeof(float);
        bd.BindFlags = D3D11_BIND_CONSTANT_BUFFER;
        bd.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;
        
        hr = device->CreateBuffer(&bd, nullptr, &constantBuffer);
        return SUCCEEDED(hr);
    }
    
    void InitLCARSElements() {
        int screenWidth = GetSystemMetrics(SM_CXSCREEN);
        int screenHeight = GetSystemMetrics(SM_CYSCREEN);
        
        // Великий верхній лівий elbow
        elements.push_back({
            XMFLOAT2(200.0f, 150.0f),
            XMFLOAT2(400.0f, 150.0f),
            palette.elbows[0],
            "elbow",
            0.0f
        });
        
        // Кнопки
        std::string buttonNames[] = {"BRIDGE", "SENSORS", "COMMS", "TACTICAL", "ENGINEERING"};
        for (int i = 0; i < 5; i++) {
            elements.push_back({
                XMFLOAT2(200.0f, 350.0f + i * 70.0f),
                XMFLOAT2(300.0f, 50.0f),
                palette.buttons[i % 4],
                "button",
                (float)i * 0.5f
            });
        }
        
        // Великий сканер
        elements.push_back({
            XMFLOAT2(650.0f, 350.0f),
            XMFLOAT2(1000.0f, 6.0f),
            palette.scanners[0],
            "scanner",
            0.0f
        });
        
        // Центральний дисплей
        elements.push_back({
            XMFLOAT2(650.0f, 400.0f),
            XMFLOAT2(1000.0f, 500.0f),
            palette.displays[0],
            "display",
            0.0f
        });
    }
    
    void AddLCARSElbowVertices(std::vector<LCARSVertex>& vertices, const LCARSElement& elem) {
        float thick = min(elem.size.x, elem.size.y) / 2.0f;
        float x = elem.position.x;
        float y = elem.position.y;
        float w = elem.size.x;
        float h = elem.size.y;
        
        // Горизонтальна частина
        vertices.push_back({XMFLOAT3(x + thick, y, 0.0f), elem.color, elem.animPhase});
        vertices.push_back({XMFLOAT3(x + w, y, 0.0f), elem.color, elem.animPhase});
        vertices.push_back({XMFLOAT3(x + w, y + thick, 0.0f), elem.color, elem.animPhase});
        vertices.push_back({XMFLOAT3(x + thick, y + thick, 0.0f), elem.color, elem.animPhase});
        
        // Вертикальна частина
        vertices.push_back({XMFLOAT3(x, y + thick, 0.0f), elem.color, elem.animPhase});
        vertices.push_back({XMFLOAT3(x + thick, y + thick, 0.0f), elem.color, elem.animPhase});
        vertices.push_back({XMFLOAT3(x + thick, y + h, 0.0f), elem.color, elem.animPhase});
        vertices.push_back({XMFLOAT3(x, y + h, 0.0f), elem.color, elem.animPhase});
        
        // Дуга - багато сегментів
        int segments = 64;
        for (int i = 0; i < segments; i++) {
            float angle1 = XM_PI/2 + (i * XM_PI/2) / segments;
            float angle2 = XM_PI/2 + ((i + 1) * XM_PI/2) / segments;
            
            float cx = x + thick;
            float cy = y + thick;
            
            float x1 = cx + thick * cos(angle1);
            float y1 = cy + thick * sin(angle1);
            float x2 = cx + thick * cos(angle2);
            float y2 = cy + thick * sin(angle2);
            
            vertices.push_back({XMFLOAT3(cx, cy, 0.0f), elem.color, elem.animPhase});
            vertices.push_back({XMFLOAT3(x1, y1, 0.0f), elem.color, elem.animPhase});
            vertices.push_back({XMFLOAT3(x2, y2, 0.0f), elem.color, elem.animPhase});
        }
    }
    
    void AddLCARSButtonVertices(std::vector<LCARSVertex>& vertices, const LCARSElement& elem) {
        float x = elem.position.x;
        float y = elem.position.y;
        float w = elem.size.x;
        float h = elem.size.y;
        
        // Градієнтна кнопка
        for (int i = 0; i < 10; i++) {
            float fade = (float)i / 10.0f;
            float x1 = x + i * (w / 10.0f);
            float x2 = x + (i + 1) * (w / 10.0f);
            
            XMFLOAT3 color1 = XMFLOAT3(
                elem.color.x * (1.0f - fade * 0.3f),
                elem.color.y * (1.0f - fade * 0.3f),
                elem.color.z * (1.0f - fade * 0.3f)
            );
            
            XMFLOAT3 color2 = XMFLOAT3(
                elem.color.x * (1.0f - (i + 1) / 10.0f * 0.3f),
                elem.color.y * (1.0f - (i + 1) / 10.0f * 0.3f),
                elem.color.z * (1.0f - (i + 1) / 10.0f * 0.3f)
            );
            
            vertices.push_back({XMFLOAT3(x1, y, 0.0f), color1, elem.animPhase});
            vertices.push_back({XMFLOAT3(x2, y, 0.0f), color2, elem.animPhase});
            vertices.push_back({XMFLOAT3(x2, y + h, 0.0f), color2, elem.animPhase});
            vertices.push_back({XMFLOAT3(x1, y + h, 0.0f), color1, elem.animPhase});
        }
    }
    
    void Render() {
        // Очищуємо екран
        float clearColor[4] = {0.0f, 0.0f, 0.0f, 1.0f};
        context->ClearRenderTargetView(renderTargetView, clearColor);
        
        // Створюємо vertices для всіх елементів
        std::vector<LCARSVertex> vertices;
        
        for (const auto& elem : elements) {
            if (elem.type == "elbow") {
                AddLCARSElbowVertices(vertices, elem);
            } else if (elem.type == "button") {
                AddLCARSButtonVertices(vertices, elem);
            }
        }
        
        // Завантажуємо vertices в buffer
        D3D11_MAPPED_SUBRESOURCE ms;
        context->Map(vertexBuffer, 0, D3D11_MAP_WRITE_DISCARD, 0, &ms);
        memcpy(ms.pData, vertices.data(), sizeof(LCARSVertex) * vertices.size());
        context->Unmap(vertexBuffer, 0);
        
        // Налаштування рендерингу
        UINT stride = sizeof(LCARSVertex);
        UINT offset = 0;
        context->IASetVertexBuffers(0, 1, &vertexBuffer, &stride, &offset);
        context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
        
        // Встановлюємо шейдери
        context->IASetInputLayout(inputLayout);
        context->VSSetShader(vertexShader, nullptr, 0);
        context->PSSetShader(pixelShader, nullptr, 0);
        
        // Оновлюємо constant buffer
        XMMATRIX world = XMMatrixIdentity();
        XMMATRIX view = XMMatrixIdentity();
        XMMATRIX proj = XMMatrixOrthographicOffCenterLH(
            0.0f, (float)GetSystemMetrics(SM_CXSCREEN),
            (float)GetSystemMetrics(SM_CYSCREEN), 0.0f,
            0.0f, 1.0f
        );
        
        XMMATRIX wvp = world * view * proj;
        
        struct ConstantBuffer {
            XMMATRIX WorldViewProj;
            float Time;
            float padding[3];
        };
        
        ConstantBuffer cb;
        cb.WorldViewProj = XMMatrixTranspose(wvp);
        cb.Time = time;
        
        context->Map(constantBuffer, 0, D3D11_MAP_WRITE_DISCARD, 0, &ms);
        memcpy(ms.pData, &cb, sizeof(cb));
        context->Unmap(constantBuffer, 0);
        context->VSSetConstantBuffers(0, 1, &constantBuffer);
        
        // Малюємо
        context->Draw(vertices.size(), 0);
        
        // Показуємо результат
        swapChain->Present(1, 0);
        
        time += 0.016f;
    }
    
    void Run() {
        ShowWindow(hWnd, SW_SHOW);
        UpdateWindow(hWnd);
        
        MSG msg = {};
        while (msg.message != WM_QUIT) {
            if (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE)) {
                TranslateMessage(&msg);
                DispatchMessage(&msg);
            } else {
                Render();
            }
        }
    }
    
    void Cleanup() {
        if (vertexBuffer) vertexBuffer->Release();
        if (constantBuffer) constantBuffer->Release();
        if (inputLayout) inputLayout->Release();
        if (vertexShader) vertexShader->Release();
        if (pixelShader) pixelShader->Release();
        if (renderTargetView) renderTargetView->Release();
        if (swapChain) swapChain->Release();
        if (context) context->Release();
        if (device) device->Release();
    }
    
    static LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
        switch (message) {
            case WM_KEYDOWN:
                if (wParam == VK_ESCAPE) {
                    PostQuitMessage(0);
                }
                break;
            case WM_DESTROY:
                PostQuitMessage(0);
                break;
            default:
                return DefWindowProc(hWnd, message, wParam, lParam);
        }
        return 0;
    }
};

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    LCARSDX11 lcars;
    
    if (!lcars.Initialize()) {
        MessageBox(nullptr, L"Failed to initialize LCARS DirectX 11", L"Error", MB_OK);
        return -1;
    }
    
    lcars.Run();
    
    return 0;
}
