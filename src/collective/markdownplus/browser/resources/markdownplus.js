(function () {
  "use strict";

  var MARKDOWN_MIME_TYPES = {
    "text/markdown": true,
    "text/x-web-markdown": true,
  };
  var instances = new WeakMap();
  var mermaidConfigured = false;

  function MarkdownPlus(textarea) {
    this.textarea = textarea;
    this.options = readPatternOptions(textarea);
    this.wrapper = null;
    this.editorPane = null;
    this.toolbar = null;
    this.preview = null;
    this.selector = null;
    this.originalParent = textarea.parentNode;
    this.originalTextareaNextSibling = textarea.nextSibling;
    this.originalSelectorParent = null;
    this.originalSelectorNextSibling = null;
    this.renderNonce = 0;
    this.onInput = this.handleInput.bind(this);
    this.onResize = this.syncPaneHeights.bind(this);
  }

  MarkdownPlus.prototype.init = function () {
    if (instances.has(this.textarea)) {
      instances.get(this.textarea).renderPreview();
      return;
    }

    this.selector = findAssociatedSelector(this.textarea);
    if (this.selector) {
      this.originalSelectorParent = this.selector.parentNode;
      this.originalSelectorNextSibling = this.selector.nextSibling;
      this.selector.classList.add("mp-mime-selector");
    }

    this.textarea.classList.add("mp-editor-input");

    this.wrapper = document.createElement("div");
    this.wrapper.className = "mp-editor-wrap";
    this.textarea.parentNode.insertBefore(this.wrapper, this.textarea);

    this.toolbar = document.createElement("div");
    this.toolbar.className = "mp-toolbar";
    this.toolbar.setAttribute("role", "toolbar");
    this.toolbar.setAttribute("aria-label", "Markdown formatting toolbar");
    this.wrapper.appendChild(this.toolbar);

    this.editorPane = document.createElement("div");
    this.editorPane.className = "mp-editor-pane";
    this.wrapper.appendChild(this.editorPane);
    this.editorPane.appendChild(this.textarea);
    if (this.selector) {
      this.editorPane.appendChild(this.selector);
    }

    this.preview = document.createElement("div");
    this.preview.className = "mp-preview";
    this.preview.setAttribute("aria-live", "polite");
    this.wrapper.appendChild(this.preview);

    this.buildToolbar();
    this.textarea.addEventListener("input", this.onInput);
    window.addEventListener("resize", this.onResize);
    this.handleInput();
    instances.set(this.textarea, this);
  };

  MarkdownPlus.prototype.destroy = function () {
    this.textarea.removeEventListener("input", this.onInput);
    window.removeEventListener("resize", this.onResize);
    this.textarea.classList.remove("mp-editor-input", "pat-markdownplus");
    this.textarea.removeAttribute("data-pat-markdownplus");
    if (this.selector) {
      this.selector.classList.remove("mp-mime-selector");
    }

    if (this.toolbar) {
      this.toolbar.remove();
      this.toolbar = null;
    }
    if (this.editorPane) {
      this.editorPane.remove();
      this.editorPane = null;
    }
    if (this.preview) {
      this.preview.remove();
      this.preview = null;
    }

    if (this.wrapper && this.wrapper.parentNode) {
      this.wrapper.parentNode.insertBefore(this.textarea, this.wrapper);
      this.wrapper.remove();
      this.wrapper = null;
    }

    if (this.selector && this.originalSelectorParent) {
      if (this.originalSelectorNextSibling && this.originalSelectorNextSibling.parentNode === this.originalSelectorParent) {
        this.originalSelectorParent.insertBefore(this.selector, this.originalSelectorNextSibling);
      } else {
        this.originalSelectorParent.appendChild(this.selector);
      }
    }

    instances.delete(this.textarea);
  };

  MarkdownPlus.prototype.buildToolbar = function () {
    var self = this;
    var actions = [
      { label: "B", title: "Bold", wrap: ["**", "**"] },
      { label: "I", title: "Italic", wrap: ["*", "*"] },
      { label: "Code", title: "Code block", wrap: ["\n```\n", "\n```\n"] },
      { label: "Link", title: "Link", wrap: ["[", "](https://example.com)"] },
    ];

    actions.forEach(function (action) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = "mp-toolbar-btn";
      button.textContent = action.label;
      button.title = action.title;
      button.addEventListener("click", function () {
        self.wrapSelection(action.wrap[0], action.wrap[1]);
      });
      self.toolbar.appendChild(button);
    });
  };

  MarkdownPlus.prototype.wrapSelection = function (prefix, suffix) {
    var start = this.textarea.selectionStart;
    var end = this.textarea.selectionEnd;
    var value = this.textarea.value;
    var selected = value.slice(start, end);
    var replacement = prefix + selected + suffix;

    this.textarea.value = value.slice(0, start) + replacement + value.slice(end);
    this.textarea.focus();
    this.textarea.selectionStart = start + prefix.length;
    this.textarea.selectionEnd = end + prefix.length;
    this.handleInput();
  };

  MarkdownPlus.prototype.handleInput = function () {
    this.autoGrow();
    this.renderPreview();
    this.syncPaneHeights();
  };

  MarkdownPlus.prototype.autoGrow = function () {
    this.textarea.style.height = "auto";
  };

  MarkdownPlus.prototype.syncPaneHeights = function () {
    if (!this.preview) {
      return;
    }

    this.preview.style.height = "auto";
    var computed = window.getComputedStyle(this.textarea);
    var minHeight = parseFloat(computed.minHeight) || 0;
    var targetHeight = Math.max(
      minHeight,
      this.textarea.scrollHeight,
      this.preview.scrollHeight
    );

    this.textarea.style.height = targetHeight + "px";
    this.preview.style.height = targetHeight + "px";
  };

  MarkdownPlus.prototype.renderPreview = function () {
    var source = this.textarea.value || "";
    var previewUrl = this.options.previewUrl;
    var currentNonce = this.renderNonce + 1;
    this.renderNonce = currentNonce;

    if (!previewUrl) {
      this.setPreviewHtml(toHtml(source));
      return;
    }

    requestServerRender(previewUrl, source, this.textarea)
      .then(function (html) {
        if (this.renderNonce !== currentNonce) {
          return;
        }
        this.setPreviewHtml(html);
      }.bind(this))
      .catch(function () {
        if (this.renderNonce !== currentNonce) {
          return;
        }
        this.setPreviewHtml(toHtml(source));
      }.bind(this));
  };

  MarkdownPlus.prototype.setPreviewHtml = function (html) {
    this.preview.innerHTML = html;
    hydrateRenderedMarkdown(this.preview);
  };

  function hydrateRenderedMarkdown(root) {
    if (!root) {
      return;
    }

    renderMath(root);
    renderMermaid(root);
  }

  function renderMath(root) {
    if (!root || typeof window.renderMathInElement !== "function") {
      return;
    }

    window.renderMathInElement(root, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "\\[", right: "\\]", display: true },
        { left: "$", right: "$", display: false },
        { left: "\\(", right: "\\)", display: false }
      ],
      throwOnError: false,
      strict: "ignore"
    });
  }

  function renderMermaid(root) {
    if (!root || !window.mermaid) {
      return;
    }

    if (!mermaidConfigured && typeof window.mermaid.initialize === "function") {
      window.mermaid.initialize({ startOnLoad: false });
      mermaidConfigured = true;
    }

    var nodes = Array.prototype.slice.call(root.querySelectorAll(".mermaid"));
    if (!nodes.length) {
      return;
    }

    if (typeof window.mermaid.run === "function") {
      window.mermaid.run({ nodes: nodes }).catch(function () {
        // Keep markdown content visible if Mermaid parsing fails.
      });
      return;
    }

    if (typeof window.mermaid.init === "function") {
      window.mermaid.init(undefined, nodes);
    }
  }

  function getCsrfToken(textarea) {
    var form = textarea && textarea.form ? textarea.form : null;
    var tokenInput = form
      ? form.querySelector('input[name="_authenticator"]')
      : document.querySelector('input[name="_authenticator"]');

    return tokenInput && tokenInput.value ? tokenInput.value : "";
  }

  function requestServerRender(previewUrl, source, textarea) {
    var token = getCsrfToken(textarea);
    var body = "text=" + encodeURIComponent(source || "");
    if (token) {
      body += "&_authenticator=" + encodeURIComponent(token);
    }

    var headers = {
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    };
    if (token) {
      headers["X-CSRF-TOKEN"] = token;
    }

    return fetch(previewUrl, {
      method: "POST",
      headers: headers,
      body: body,
      credentials: "same-origin",
    }).then(function (response) {
      if (!response.ok) {
        throw new Error("Preview request failed");
      }
      return response.json();
    }).then(function (payload) {
      return payload && payload.html ? payload.html : "";
    });
  }

  function readPatternOptions(textarea) {
    var raw = textarea.getAttribute("data-pat-markdownplus");
    if (!raw) {
      return {};
    }

    try {
      return JSON.parse(raw);
    } catch (error) {
      return {};
    }
  }

  function inferPreviewUrl(textarea) {
    var action = textarea && textarea.form ? (textarea.form.getAttribute("action") || "") : "";
    var current = action || window.location.href || "";

    // Remove query/hash and trailing /edit so the preview endpoint targets context.
    current = current.split("#")[0].split("?")[0];
    current = current.replace(/\/edit$/, "");

    if (!current) {
      return "";
    }
    return current + "/@@markdownplus-preview";
  }

  function escapeHtml(value) {
    return value
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function parseInline(value) {
    var placeholders = [];
    var html = escapeHtml(value || "");

    html = html.replace(/`([^`]+)`/g, function (_, code) {
      var token = "@@MP_CODE_" + placeholders.length + "@@";
      placeholders.push('<code class="mp-inline-code">' + code + "</code>");
      return token;
    });

    html = html.replace(/\[([^\]]+)\]\(([^)\s]+(?:\s+"[^"]*")?)\)/g, function (_, text, url) {
      return '<a href="' + url + '" target="_blank" rel="noreferrer noopener">' + text + "</a>";
    });
    html = html.replace(/~~(.+?)~~/g, '<del class="mp-del">$1</del>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="mp-strong">$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em class="mp-em">$1</em>');

    placeholders.forEach(function (snippet, index) {
      html = html.replace("@@MP_CODE_" + index + "@@", snippet);
    });

    return html;
  }

  function splitTableRow(line) {
    var trimmed = (line || "").trim();
    if (trimmed.charAt(0) === "|") {
      trimmed = trimmed.slice(1);
    }
    if (trimmed.charAt(trimmed.length - 1) === "|") {
      trimmed = trimmed.slice(0, -1);
    }
    return trimmed.split("|").map(function (cell) {
      return cell.trim();
    });
  }

  function isTableSeparatorLine(line) {
    var trimmed = (line || "").trim();
    if (!trimmed || trimmed.indexOf("|") === -1) {
      return false;
    }
    return /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(trimmed);
  }

  function parseTableAlignments(separatorLine) {
    return splitTableRow(separatorLine).map(function (cell) {
      var left = cell.charAt(0) === ":";
      var right = cell.charAt(cell.length - 1) === ":";
      if (left && right) {
        return "center";
      }
      if (right) {
        return "right";
      }
      if (left) {
        return "left";
      }
      return "";
    });
  }

  function parseBlocks(markdown) {
    var lines = (markdown || "").replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
    var i = 0;
    var html = [];

    function isBlank(line) {
      return !line || /^\s*$/.test(line);
    }

    while (i < lines.length) {
      var line = lines[i] || "";

      if (isBlank(line)) {
        i += 1;
        continue;
      }

      if (/^```/.test(line)) {
        var info = line.replace(/^```\s*/, "").trim();
        var codeLines = [];
        i += 1;
        while (i < lines.length && !/^```/.test(lines[i])) {
          codeLines.push(lines[i]);
          i += 1;
        }
        if (i < lines.length) {
          i += 1;
        }
        var languageClass = info ? ' class="language-' + escapeHtml(info) + '"' : "";
        html.push('<pre class="mp-code"><code' + languageClass + ">" + escapeHtml(codeLines.join("\n")) + "</code></pre>");
        continue;
      }

      var heading = /^(#{1,6})\s+(.*)$/.exec(line);
      if (heading) {
        var level = heading[1].length;
        var headingClass = level <= 3 ? ' class="mp-h' + level + '"' : "";
        html.push("<h" + level + headingClass + ">" + parseInline(heading[2].trim()) + "</h" + level + ">");
        i += 1;
        continue;
      }

      if (/^\s*([-*_])\s*\1\s*\1([\s\1]*)$/.test(line)) {
        html.push('<hr class="mp-hr" />');
        i += 1;
        continue;
      }

      if (line.indexOf("|") !== -1 && i + 1 < lines.length && isTableSeparatorLine(lines[i + 1])) {
        var headers = splitTableRow(line);
        var aligns = parseTableAlignments(lines[i + 1]);
        var bodyRows = [];
        i += 2;
        while (i < lines.length && lines[i].indexOf("|") !== -1 && !isBlank(lines[i])) {
          bodyRows.push(splitTableRow(lines[i]));
          i += 1;
        }

        var table = ['<table class="mp-table"><thead><tr>'];
        headers.forEach(function (cell, index) {
          var align = aligns[index] ? ' style="text-align:' + aligns[index] + '"' : "";
          table.push("<th" + align + ">" + parseInline(cell) + "</th>");
        });
        table.push("</tr></thead>");
        if (bodyRows.length) {
          table.push("<tbody>");
          bodyRows.forEach(function (row) {
            table.push("<tr>");
            row.forEach(function (cell, index) {
              var align = aligns[index] ? ' style="text-align:' + aligns[index] + '"' : "";
              table.push("<td" + align + ">" + parseInline(cell) + "</td>");
            });
            table.push("</tr>");
          });
          table.push("</tbody>");
        }
        table.push("</table>");
        html.push(table.join(""));
        continue;
      }

      var ulMatch = /^\s*[-*+]\s+(.+)$/.exec(line);
      var olMatch = /^\s*\d+\.\s+(.+)$/.exec(line);
      if (ulMatch || olMatch) {
        var isOrdered = !!olMatch;
        var tag = isOrdered ? "ol" : "ul";
        var items = [];

        while (i < lines.length) {
          var current = lines[i] || "";
          var match = isOrdered
            ? /^\s*\d+\.\s+(.+)$/.exec(current)
            : /^\s*[-*+]\s+(.+)$/.exec(current);
          if (!match) {
            break;
          }
          var itemText = match[1];
          var taskMatch = /^\[( |x|X)\]\s+(.+)$/.exec(itemText);
          if (taskMatch) {
            var checked = taskMatch[1].toLowerCase() === "x";
            items.push(
              '<li class="mp-task-item"><input type="checkbox" disabled="disabled"'
              + (checked ? ' checked="checked"' : "")
              + " /> "
              + parseInline(taskMatch[2])
              + "</li>"
            );
          } else {
            items.push("<li>" + parseInline(itemText) + "</li>");
          }
          i += 1;
        }

        html.push("<" + tag + " class=\"mp-list\">" + items.join("") + "</" + tag + ">");
        continue;
      }

      if (/^\s*>\s?/.test(line)) {
        var quoteLines = [];
        while (i < lines.length && /^\s*>\s?/.test(lines[i])) {
          quoteLines.push(lines[i].replace(/^\s*>\s?/, ""));
          i += 1;
        }
        html.push('<blockquote class="mp-quote">' + parseBlocks(quoteLines.join("\n")) + "</blockquote>");
        continue;
      }

      var paragraphLines = [line];
      i += 1;
      while (i < lines.length && !isBlank(lines[i])) {
        if (/^```/.test(lines[i])) {
          break;
        }
        paragraphLines.push(lines[i]);
        i += 1;
      }

      html.push("<p>" + parseInline(paragraphLines.join("\n")).replace(/\n/g, "<br />") + "</p>");
    }

    return html.join("\n");
  }

  function toHtml(markdown) {
    return parseBlocks(markdown || "");
  }

  function enableForTextarea(textarea) {
    if (!instances.has(textarea)) {
      var instance = new MarkdownPlus(textarea);
      instance.init();
    } else {
      instances.get(textarea).handleInput();
    }
  }

  function disableForTextarea(textarea) {
    var instance = instances.get(textarea);
    if (instance) {
      instance.destroy();
    }
  }

  function findTargetTextareasForSelect(select) {
    var textareaName = select.name.replace(/\.mimeType$/, "");
    if (!textareaName) {
      return [];
    }
    return Array.prototype.slice.call(
      document.querySelectorAll('textarea[name="' + textareaName + '"]')
    );
  }

  function findAssociatedSelector(textarea) {
    if (!textarea.name) {
      return null;
    }
    return document.querySelector(
      'select.pat-textareamimetypeselector[name="' + textarea.name + '.mimeType"]'
    );
  }

  function syncForSelector(select) {
    var isMarkdown = !!MARKDOWN_MIME_TYPES[select.value];
    findTargetTextareasForSelect(select).forEach(function (textarea) {
      if (isMarkdown) {
        var options = readPatternOptions(textarea);
        if (!options.previewUrl) {
          options.previewUrl = inferPreviewUrl(textarea);
        }
        textarea.classList.add("pat-markdownplus");
        textarea.setAttribute("data-pat-markdownplus", JSON.stringify(options));
        enableForTextarea(textarea);
      } else {
        disableForTextarea(textarea);
      }
    });
  }

  function bindSelector(select) {
    if (select.dataset.markdownplusBound === "1") {
      return;
    }
    select.dataset.markdownplusBound = "1";
    select.addEventListener("input", function () {
      syncForSelector(select);
    });
    select.addEventListener("change", function () {
      syncForSelector(select);
    });
    syncForSelector(select);
  }

  function scanAndBind() {
    document
      .querySelectorAll("select.pat-textareamimetypeselector")
      .forEach(bindSelector);

    document.querySelectorAll("textarea.pat-markdownplus").forEach(function (textarea) {
      enableForTextarea(textarea);
    });

    hydrateRenderedMarkdown(document.body || document);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scanAndBind);
  } else {
    scanAndBind();
  }

  document.addEventListener("pat-update", scanAndBind);
})();
