import * as qvac from "@qvac/sdk";
import fs from "node:fs";

const out = [];

out.push("QVAC MODEL DUMP");
out.push("================");
out.push("");
out.push(`Total models: ${qvac.models.length}`);
out.push("");

for (let i = 0; i < qvac.models.length; i++) {
    const model = qvac.models[i];

    out.push("############################################################");
    out.push(`# MODEL ${i}`);
    out.push("############################################################");

    try {
        out.push(`TYPE: ${typeof model}`);
        out.push("");

        if (typeof model === "object" && model !== null) {

            try {
                out.push("JSON:");
                out.push(JSON.stringify(model, null, 2));
            } catch (e) {
                out.push("JSON ERROR:");
                out.push(String(e));
            }

            out.push("");
            out.push("KEYS:");

            for (const key of Object.keys(model)) {
                try {
                    out.push(`${key} = ${String(model[key])}`);
                } catch {
                    out.push(`${key} = <unprintable>`);
                }
            }

        } else {

            out.push(String(model));

        }

    } catch (err) {

        out.push("ERROR:");
        out.push(String(err));

    }

    out.push("");
}

fs.writeFileSync(
    "qvac-models-full.txt",
    out.join("\n"),
    "utf8"
);

console.log(`Saved ${qvac.models.length} models`);
console.log("File: qvac-models-full.txt");
