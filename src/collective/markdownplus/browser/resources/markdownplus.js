(function () {
  "use strict";

  var MARKDOWN_MIME_TYPES = {
    "text/markdown": true,
    "text/x-web-markdown": true,
  };
  var instances = new WeakMap();

  function MarkdownPlus(textarea) {
    this.textarea = textarea;
    this.wrapper = null;
    this.toolbar = null;
    this.preview = null;
    this.onInput = this.renderPreview.bind(this);
  }

  MarkdownPlus.prototype.init = function () {
    if (instances.has(this.textarea)) {
      instances.get(this.textarea).renderPreview();
      return;
    }

    this.textarea.classList.add("mp-editor-input");

    this.wrapper = document.createElement("div");
    this.wrapper.className = "mp-editor-wrap";
    this.textarea.parentNode.insertBefore(this.wrapper, this.textarea);
    this.wrapper.appendChild(this.textarea);

    this.toolbar = document.createElement("div");
    this.toolbar.className = "mp-toolbar";
    this.toolbar.setAttribute("role", "toolbar");
    this.toolbar.setAttribute("aria-label", "Markdown formatting toolbar");
    this.wrapper.insertBefore(this.toolbar, this.textarea);

    this.preview = document.createElement("div");
    this.preview.className = "mp-preview";
    this.preview.setAttribute("aria-live", "polite");
    this.wrapper.appendChild(this.preview);

    this.buildToolbar();
    this.textarea.addEventListener("input", this.onInput);
    this.renderPreview();
    instances.set(this.textarea, this);
  };

  MarkdownPlus.prototype.destroy = function () {
    this.textarea.removeEventListener("input", this.onInput);
    this.textarea.classList.remove("mp-editor-input", "pat-markdownplus");
    this.textarea.removeAttribute("data-pat-markdownplus");

    if (this.toolbar) {
      this.toolbar.remove();
      this.toolbar = null;
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
    this.renderPreview();
  };

  MarkdownPlus.prototype.renderPreview = function () {
    var source = this.textarea.value || "";
    this.preview.innerHTML = toHtml(source);
  };

  function escapeHtml(value) {
    return value
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function toHtml(markdown) {
    var escaped = escapeHtml(markdown);

    escaped = escaped.replace(/```([\s\S]*?)```/g, function (_, block) {
      return '<pre class="mp-code"><code>' + block + "</code></pre>";
    });
    escaped = escaped.replace(/^###\s+(.*)$/gm, '<h3 class="mp-h3">$1</h3>');
    escaped = escaped.replace(/^##\s+(.*)$/gm, '<h2 class="mp-h2">$1</h2>');
    escaped = escaped.replace(/^#\s+(.*)$/gm, '<h1 class="mp-h1">$1</h1>');
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong class="mp-strong">$1</strong>');
    escaped = escaped.replace(/\*(.*?)\*/g, '<em class="mp-em">$1</em>');
    escaped = escaped.replace(/`([^`]+)`/g, '<code class="mp-inline-code">$1</code>');
    escaped = escaped.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');

    return escaped
      .split(/\n\s*\n/)
      .map(function (chunk) {
        if (/^\s*<h[1-3]|^\s*<pre/.test(chunk)) {
          return chunk;
        }
        return "<p>" + chunk.replace(/\n/g, "<br />") + "</p>";
      })
      .join("\n");
  }

  function enableForTextarea(textarea) {
    if (!instances.has(textarea)) {
      var instance = new MarkdownPlus(textarea);
      instance.init();
    } else {
      instances.get(textarea).renderPreview();
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

  function syncForSelector(select) {
    var isMarkdown = !!MARKDOWN_MIME_TYPES[select.value];
    findTargetTextareasForSelect(select).forEach(function (textarea) {
      if (isMarkdown) {
        textarea.classList.add("pat-markdownplus");
        textarea.setAttribute("data-pat-markdownplus", '{"preview": true, "theme": "light"}');
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
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scanAndBind);
  } else {
    scanAndBind();
  }

  document.addEventListener("pat-update", scanAndBind);
})();
