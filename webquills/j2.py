# vim: set fileencoding=utf-8 :
#
#   Copyright 2016 Vince Veselosky and contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import urllib.parse as uri
from pathlib import Path

import jinja2
import jmespath

from webquills.util import getLogger


def jmes(struct, query):
    # Reverses order of arguments for use as filter inside Jinja templates
    return jmespath.search(query, struct)


def absolute(relative, base):
    return uri.urljoin(base, relative)


def with_suffix(filename, suffix):
    return Path(filename).with_suffix(suffix)


def render(config, context, templatename):
    # TODO Hard-coded FSLoader very limiting. Allow other loaders by config.
    # Certainly we will want package loader, possibly S3 loader.
    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(config["jinja2"]["templatedir"]))
    jinja.filters["jmes"] = jmes
    jinja.filters["absolute"] = absolute
    jinja.filters["with_suffix"] = with_suffix
    template = jinja.get_or_select_template(templatename)
    return template.render(context)


def templates_from_context(ctx):
    # In the webquills.ini, create a jinja2_templates section. Each key is a
    # filename extension, e.g. "html". The value is a space-separated list of
    # possible template names. The first template in this list found to exist
    # will be used to render an output with that extension.
    # Default HTML templates will be added.
    templates = ctx.get("jinja2_templates", {})
    pieces = ctx["Item"]["itemtype"].split("/")
    logger = getLogger()
    logger.debug("templates from context: " + repr(pieces))
    while pieces:
        for extension in ctx["Webquills"]["scribes"]:
            filename = "_".join(pieces) + "." + extension + ".j2"
            templates.setdefault(extension, []).append(filename)
        pieces.pop()
    # TODO Allow template overrides
    logger.debug("templates from context: " + repr(templates))
    return templates
