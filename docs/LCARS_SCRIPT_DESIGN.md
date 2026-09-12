# LCARS Script - Мова програмування для наукових симуляцій

## Огляд

LCARS Script - це спеціалізована мова програмування, розроблена для LCARS Framework, що поєднує естетику Star Trek інтерфейсів з потужністю наукових обчислень, особливо для Geant4 симуляцій.

## Філософія дизайну

1. **Декларативність** - фокус на що робити, а не як
2. **Вбудована підтримка симуляцій** - спеціальні конструкції для наукових обчислень
3. **Event-driven архітектура** - інтеграція з існуючим EventBus
4. **Фізична типізація** - одиниці виміру, константи, перевірка розмірностей
5. **Візуальна сумісність** - синтаксис відображає LCARS естетику

## Синтаксис та конструкції

### 1. Базові декларації

```lcars
// Фізичні величини з одиницями виміру
beam_energy: 1.5 GeV
particle_count: 10000
magnetic_field: 3.8 T
detector_length: 2.5 m

// Стандартні змінні
simulation_name: "main_beam_test"
output_directory: "/data/simulations/"
```

### 2. Симуляції

```lcars
SIMULATION main_beam {
    // Параметри симуляції
    ENERGY beam_energy
    PARTICLES particle_count
    GEOMETRY "cms_detector.geo"
    
    // Обробники подій
    ON START {
        log("Initializing beam simulation...")
        configure_detector()
        emit("detector:ready")
    }
    
    ON PROGRESS(percent) {
        update_ui("progress", percent)
        log("Simulation progress: " + percent + "%")
    }
    
    ON COMPLETE {
        analyze_results()
        export_data("output.root")
        emit("simulation:complete", {
            duration: elapsed_time,
            events: processed_events
        })
    }
    
    ON ERROR {
        log("Simulation failed: " + error.message)
        emit("simulation:error", {details: error})
    }
}
```

### 3. Детектори

```lcars
DETECTOR cms_detector {
    LAYERS [
        {
            type: "pixel_silicon",
            thickness: 300 μm,
            position: [0, 0, 0],
            material: "silicon"
        },
        {
            type: "ecal",
            thickness: 20 cm,
            position: [0, 0, 1.5m],
            material: "lead_tungstate"
        }
    ]
    
    MAGNETIC_FIELD 3.8 T
    TEMPERATURE -20°C
    READOUT "digital"
    
    ON HIT(particle) {
        record_hit(particle.position, particle.energy, particle.time)
        emit("detector:hit", particle)
    }
}
```

### 4. Аналіз даних

```lcars
ANALYZER energy_spectrum {
    INPUT "simulation_output.root"
    
    PROCESS {
        // Створення гістограми
        spectrum = create_histogram(
            "energy_spectrum", 
            bins: 100, 
            range: [0, 5 GeV]
        )
        
        // Заповнення даними
        foreach event in input.events {
            spectrum.fill(event.particle.energy)
        }
        
        // Підгонка кривої
        fit_result = fit_gaussian(spectrum)
        peak_energy = fit_result.mean
        resolution = fit_result.sigma / fit_result.mean
        
        // Експорт результатів
        export_plot(spectrum, "plots/energy_spectrum.png")
        export_data({
            peak: peak_energy,
            resolution: resolution,
            chi2: fit_result.chi2
        }, "results/energy_analysis.json")
    }
}
```

### 5. Візуалізація

```lcars
VISUALIZE detector_3d {
    TYPE "3d_model"
    SOURCE cms_detector
    STYLE "lcars_tng"
    
    OPTIONS {
        rotation: true,
        transparency: 0.7,
        color_scheme: "enterprise_blue"
    }
    
    EXPORT "models/detector.glb"
    
    ON READY {
        show_in_ui("3d_viewer")
        emit("visualization:ready")
    }
}
```

### 6. Функції та процедури

```lcars
FUNCTION calculate_efficiency(detected, total) -> float {
    if total == 0 return 0.0
    return detected / total * 100%
}

PROCEDURE configure_detector() {
    load_geometry("cms_detector.geo")
    setup_magnetic_field(3.8 T)
    initialize_readout()
    
    emit("detector:configured")
}

// Рекурсивна функція
FUNCTION fibonacci(n) -> int {
    if n <= 1 return n
    return fibonacci(n-1) + fibonacci(n-2)
}
```

### 7. Умовні конструкції та цикли

```lcars
IF beam_energy > 1 TeV {
    log("High energy beam detected")
    enable_safety_protocols()
} ELSE {
    log("Standard energy beam")
}

FOR i FROM 1 TO 10 {
    run_simulation(energy: i * 100 MeV)
}

WHILE simulation.running {
    update_progress()
    check_errors()
}

FOREACH particle IN event.particles {
    analyze_particle(particle)
}
```

### 8. Масиви та структури даних

```lcars
// Масиви
energies = [1 GeV, 2 GeV, 5 GeV, 10 GeV]
positions = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]

// Словники
detector_config = {
    "type": "cms",
    "magnetic_field": 3.8 T,
    "layers": 4,
    "material": "silicon"
}

// Доступ до елементів
first_energy = energies[0]
field_strength = detector_config["magnetic_field"]
```

## Вбудовані типи даних та одиниці виміру

### Фізичні одиниці

- **Енергія:** eV, keV, MeV, GeV, TeV
- **Довжина:** mm, cm, m, km, μm, nm
- **Час:** ns, μs, ms, s, min, h
- **Маса:** eV/c², MeV/c², GeV/c², kg, g
- **Заряд:** e, C
- **Магнітне поле:** T, G
- **Температура:** K, °C

### Стандартні типи

- `int` - цілі числа
- `float` - числа з плаваючою точкою
- `string` - текстові рядки
- `bool` - логічні значення
- `array` - масиви
- `dict` - словники
- `event` - події симуляції
- `particle` - частинки
- `detector` - детектори

## Інтеграція з LCARS Framework

### EventBus інтеграція

```lcars
// Генерація подій
emit("simulation:started", {
    energy: beam_energy,
    particles: particle_count
})

// Підписка на події
ON EVENT "detector:hit" {
    process_hit(event.data)
}

ON EVENT "ui:theme_changed" {
    update_visualization_style(event.data.theme)
}
```

### Плагін система

```lcars
PLUGIN custom_analyzer {
    VERSION "1.0.0"
    AUTHOR "LCARS Team"
    
    ON LOAD {
        register_analyzer("custom_energy_spectrum")
    }
    
    FUNCTION analyze(data) -> results {
        // Кастомний аналіз
        return processed_results
    }
}
```

## Приклади використання

### Проста симуляція

```lcars
// Простий тест детектора
energy: 1 GeV
particles: 1000

SIMULATION simple_test {
    ENERGY energy
    PARTICLES particles
    
    ON COMPLETE {
        efficiency = calculate_efficiency(detected, particles)
        log("Detection efficiency: " + efficiency + "%")
    }
}
```

### Складний аналіз

```lcars
// Комплексний аналіз енергетичного спектру
SIMULATION energy_scan {
    FOR energy IN [1 GeV, 2 GeV, 5 GeV, 10 GeV] {
        RUN_SINGLE {
            ENERGY energy
            PARTICLES 10000
            
            ON COMPLETE {
                analyze_spectrum(energy)
            }
        }
    }
}

ANALYZER spectrum_analysis {
    PROCESS {
        results = []
        
        FOREACH energy IN scan_energies {
            data = load_results("energy_" + energy + "_GeV.root")
            spectrum = extract_spectrum(data)
            peak = find_peak(spectrum)
            
            results.append({
                energy: energy,
                peak_position: peak.position,
                resolution: peak.resolution
            })
        }
        
        plot_resolution_curve(results)
        export_results(results, "energy_scan_results.json")
    }
}
```

## Компіляція та виконання

### Процес компіляції

1. **Лексичний аналіз** - токенізація коду
2. **Синтаксичний аналіз** - побудова AST
3. **Семантичний аналіз** - перевірка типів та одиниць
4. **Генерація коду** - створення Python коду
5. **Інтеграція** - підключення до LCARS Framework

### Запуск

```bash
# Компіляція LCARS Script
lcars-compile simulation.lcars --output simulation.py

# Запуск через LCARS Framework
python start.py --script simulation.lcars

# Інтерактивний режим
lcars-repl
```

## Переваги LCARS Script

1. **Спеціалізація** - оптимізована для наукових симуляцій
2. **Інтеграція** - глибока інтеграція з LCARS Framework
3. **Безпека** - перевірка фізичних розмірностей
4. **Продуктивність** - компіляція в оптимізований Python
5. **Екосистема** - доступ до всіх плагінів та компонентів LCARS
6. **Візуальність** - синтаксис відображає Star Trek естетику

---

*LCARS Script v1.0 - Enterprise Edition*
