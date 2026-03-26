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
    this.editorPane = null;
    this.toolbar = null;
    this.preview = null;
    this.selector = null;
    this.originalParent = textarea.parentNode;
    this.originalTextareaNextSibling = textarea.nextSibling;
    this.originalSelectorParent = null;
    this.originalSelectorNextSibling = null;
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
