#encoding: utf-8
"""Tornado handlers for the terminal emulator."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from tornado import web
from ..base.handlers import IPythonHandler, PrefixStaticHandler, path_regex
from ..utils import url_escape

class EditorHandler(PrefixStaticHandler):
    """Render the text editor interface."""

    def get(self, path):
        path = path.strip('/')
        if not self.contents_manager.file_exists(path):
            raise web.HTTPError(404, u'File does not exist: %s' % path)

        basename = path.rsplit('/', 1)[-1]
        self.write(self.render_template('edit.html',
            file_path=url_escape(path),
            basename=basename,
            page_title=basename + " (editing)",
            )
        )

default_handlers = [
    (r"/edit%s" % path_regex, EditorHandler),
]