/* 
  Minimal markdown → DOM renderer
  Usage:
    import { display } from "./markdownDisplay.js";
    display("file.md", document.getElementById("target"));
*/

export async function display(mdPath, targetElement) {
	if (!targetElement) {
		throw new Error("display(): targetElement is required");
	}

	const md = await fetchMarkdown(mdPath);
	const nodes = markdownToNodes(md);

	targetElement.innerHTML = "";
	targetElement.append(...nodes);
}

/* ---------- helpers ---------- */

async function fetchMarkdown(path) {
	const res = await fetch(path);
	if (!res.ok) {
		throw new Error(`Failed to load ${path}`);
	}
	return await res.text();
}

function markdownToNodes(markdown) {
	const lines = markdown.split(/\r?\n/);
	const nodes = [];

	let i = 0;
	while (i < lines.length) {
		const line = lines[i];

		/* ---------- headings ---------- */
		if (/^#{1,6}\s/.test(line)) {
			const level = line.match(/^#+/)[0].length;
			const el = document.createElement(`h${level}`);
			el.textContent = line.replace(/^#{1,6}\s*/, "");
			nodes.push(el);
			i++;
			continue;
		}

		/* ---------- unordered list ---------- */
		if (/^\s*-\s+/.test(line)) {
			const ul = document.createElement("ul");

			while (i < lines.length && /^\s*-\s+/.test(lines[i])) {
				const li = document.createElement("li");
				li.textContent = lines[i].replace(/^\s*-\s+/, "");
				ul.appendChild(li);
				i++;
			}

			nodes.push(ul);
			continue;
		}

		/* ---------- code block ---------- */
		if (/^```/.test(line)) {
			const pre = document.createElement("pre");
			const code = document.createElement("code");
			i++;

			while (i < lines.length && !/^```/.test(lines[i])) {
				code.textContent += lines[i] + "\n";
				i++;
			}

			pre.appendChild(code);
			nodes.push(pre);
			i++; // skip closing ```
			continue;
		}

		/* ---------- paragraph ---------- */
		if (line.trim() !== "") {
			const p = document.createElement("p");
			p.textContent = line;
			nodes.push(p);
			i++;
			continue;
		}

		i++;
	}

	return nodes;
}
