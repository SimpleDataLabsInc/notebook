"""Tornado handlers for the live notebook view."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from collections import namedtuple
import os
from tornado import web
HTTPError = web.HTTPError

from ..base.handlers import (
    IPythonHandler, FilesRedirectHandler, path_regex,
)
from ..utils import url_escape
from ..transutils import _


def get_custom_frontend_exporters():
    from nbconvert.exporters.base import get_export_names, get_exporter

    ExporterInfo = namedtuple('ExporterInfo', ['name', 'display'])

    for name in sorted(get_export_names()):
        exporter = get_exporter(name)()
        ux_name = getattr(exporter, 'export_from_notebook', None)
        if ux_name is not None:
            display = _('{} ({})'.format(ux_name, exporter.file_extension))
            yield ExporterInfo(name, display)


class NotebookHandler(IPythonHandler):

    # def static_url(self, path, include_host=None, **kwargs):
    #     prefix = self.get_query_argument("prefix", "")
    #     static_url = super(NotebookHandler, self).static_url(path, include_host, **kwargs)
    #     return prefix + static_url

    def get(self, path):
        """get renders the notebook template if a name is given, or 
        redirects to the '/files/' handler if the name is not given."""
        path = path.strip('/')
        cm = self.contents_manager
        # url_prefix = self.get_query_argument("prefix", "")

        # will raise 404 on not found
        try:
            model = cm.get(path, content=False)
        except web.HTTPError as e:
            if e.status_code == 404 and 'files' in path.split('/'):
                # 404, but '/files/' in URL, let FilesRedirect take care of it
                return FilesRedirectHandler.redirect_to_files(self, path)
            else:
                raise
        if model['type'] != 'notebook':
            # not a notebook, redirect to files
            return FilesRedirectHandler.redirect_to_files(self, path)
        name = path.rsplit('/', 1)[-1]
        self.write(self.render_template('notebook.html',
            notebook_path=path,
            notebook_name=name,
            kill_kernel=False,
            mathjax_url=self.mathjax_url,
            mathjax_config=self.mathjax_config,
            get_custom_frontend_exporters=get_custom_frontend_exporters
            )
        )


#-----------------------------------------------------------------------------
# URL to handler mappings
#-----------------------------------------------------------------------------


default_handlers = [
    (r"/notebooks%s" % path_regex, NotebookHandler),
]

