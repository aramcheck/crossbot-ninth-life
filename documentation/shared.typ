#let data = json("data.json")
#let provenance = [Data: `words_alpha.txt` (370,105 surviving lines), seed 0 unless stated, 5 s per run; Apple-vendor aarch64 Linux VM (5 vCPUs, 7.9 GiB), CPython 3.14.7.]
#let measured-caption(body, extra: none) = [#body #provenance #if extra != none { extra }]
#let diagram(file, caption) = figure(image("diagrams/" + file, width: 100%), caption: caption)
#let seconds(value) = str(calc.round(value, digits: 3)) + " s"
