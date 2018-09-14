# -*- coding: utf-8 -*-
'''
General documentation architecture:
'''
from __future__ import print_function
from __future__ import unicode_literals

import re
import inspect
import os
import shutil

import pyaer
from pyaer import device
from pyaer import dvs128
from pyaer import davis
from pyaer import edvs
from pyaer import dynapse
from pyaer import filters
from pyaer import log
from pyaer import utils

import sys
if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf8')


EXCLUDE = {
    'Optimizer',
    'Wrapper',
    'get_session',
    'set_session',
    'CallbackList',
    'serialize',
    'deserialize',
    'get',
    'set_image_dim_ordering',
    'normalize_data_format',
    'image_dim_ordering',
    'get_variable_shape',
}


# For each class to document, it is possible to:
# 1) Document only the class: [classA, classB, ...]
# 2) Document all its methods: [classA, (classB, "*")]
# 3) Choose which methods to document (methods listed as strings):
# [classA, (classB, ["method1", "method2", ...]), ...]
# 4) Choose which methods to document (methods listed as qualified names):
# [classA, (classB, [module.classB.method1, module.classB.method2, ...]), ...]
PAGES = [
    {
        'page': 'usb-device.md',
        'classes': [
            device.USBDevice,
        ],
        'methods': [
            device.USBDevice.open,
            device.USBDevice.close,
            device.USBDevice.shutdown,
            device.USBDevice.data_start,
            device.USBDevice.data_stop,
            device.USBDevice.send_default_config,
            device.USBDevice.set_data_exchange_blocking,
            device.USBDevice.set_config,
            device.USBDevice.get_config,
            device.USBDevice.get_event,
            device.USBDevice.get_packet_container,
            device.USBDevice.get_packet_header,
            device.USBDevice.get_event_packet,
            device.USBDevice.get_polarity_event,
            device.USBDevice.get_special_event,
            device.USBDevice.get_frame_event,
            device.USBDevice.get_imu6_event,
            device.USBDevice.get_spike_event,
        ],
    },
    {
        'page': 'serial-device.md',
        'classes': [
            device.SerialDevice,
        ],
        'methods': [
            device.SerialDevice.open,
            device.SerialDevice.close,
            device.SerialDevice.shutdown,
            device.SerialDevice.data_start,
            device.SerialDevice.data_stop,
            device.SerialDevice.send_default_config,
            device.SerialDevice.set_data_exchange_blocking,
            device.SerialDevice.set_config,
            device.SerialDevice.get_config,
            device.SerialDevice.get_packet_container,
            device.SerialDevice.get_packet_header,
            device.SerialDevice.get_polarity_event,
        ],
    },
    {
        'page': 'dvs128.md',
        'classes': [
            dvs128.DVS128,
        ],
        'methods': [
            dvs128.DVS128.set_noise_filter,
            dvs128.DVS128.enable_noise_filter,
            dvs128.DVS128.disable_noise_filter,
            dvs128.DVS128.obtain_device_info,
            dvs128.DVS128.open,
            dvs128.DVS128.set_bias_from_json,
            dvs128.DVS128.set_bias,
            dvs128.DVS128.get_bias,
            dvs128.DVS128.save_bias_to_json,
            dvs128.DVS128.start_data_stream,
            dvs128.DVS128.get_polarity_event,
            dvs128.DVS128.get_event,
        ],
    },
    {
        'page': 'davis.md',
        'classes': [
            davis.DAVIS,
            davis.DAVISFX2,
            davis.DAVISFX3,
            davis.DAVISRPI,
        ],
        'methods': [
            davis.DAVIS.set_noise_filter,
            davis.DAVIS.enable_noise_filter,
            davis.DAVIS.disable_noise_filter,
            davis.DAVIS.obtain_device_info,
            davis.DAVIS.open,
            davis.DAVIS.set_bias_from_json,
            davis.DAVIS.set_cf_bias,
            davis.DAVIS.set_bias,
            davis.DAVIS.get_cf_bias,
            davis.DAVIS.get_bias,
            davis.DAVIS.save_bias_to_json,
            davis.DAVIS.start_data_stream,
            davis.DAVIS.get_polarity_event,
            davis.DAVIS.get_event,
        ],
    },
    {
        'page': 'edvs.md',
        'classes': [
            edvs.eDVS,
        ],
        'methods': [
            edvs.eDVS.obtain_device_info,
            edvs.eDVS.open,
            edvs.eDVS.set_bias_from_json,
            edvs.eDVS.set_bias,
            edvs.eDVS.get_bias,
            edvs.eDVS.save_bias_to_json,
            edvs.eDVS.start_data_stream,
            edvs.eDVS.get_event,
        ],
    },
    {
        'page': 'dynapse.md',
        'classes': [
            dynapse.DYNAPSE,
        ],
        'methods': [
            dynapse.DYNAPSE.obtain_device_info,
            dynapse.DYNAPSE.open,
            dynapse.DYNAPSE.set_bias_from_json,
            dynapse.DYNAPSE.clear_sram,
            dynapse.DYNAPSE.setup_sram,
            dynapse.DYNAPSE.set_chip_bias,
            dynapse.DYNAPSE.set_bias,
            dynapse.DYNAPSE.set_fpga_bias,
            dynapse.DYNAPSE.set_activity_bias,
            dynapse.DYNAPSE.get_cf_bias,
            dynapse.DYNAPSE.get_fpga_bias,
            dynapse.DYNAPSE.save_fpga_bias_to_json,
            dynapse.DYNAPSE.start_data_stream,
            dynapse.DYNAPSE.core_xy_to_neuron_id,
            dynapse.DYNAPSE.core_id_to_neuron_id,
            dynapse.DYNAPSE.write_poisson_spikerate,
            dynapse.DYNAPSE.write_sram_N,
            dynapse.DYNAPSE.write_cam,
            dynapse.DYNAPSE.get_event,
        ],
    },
    {
        'page': 'filters.md',
        'classes': [
            filters.DVSNoise,
        ],
        'methods': [
            filters.DVSNoise.initialize,
            filters.DVSNoise.destroy,
            filters.DVSNoise.set_bias_from_json,
            filters.DVSNoise.set_bias,
            filters.DVSNoise.get_bias,
            filters.DVSNoise.save_bias_to_json,
            filters.DVSNoise.set_config,
            filters.DVSNoise.get_config,
            filters.DVSNoise.apply,
            filters.DVSNoise.get_hot_pixels,
        ],
    },
]

ROOT = 'https://dgyblog.com/pyaer-docs'


def get_function_signature(function, method=True):
    wrapped = getattr(function, '_original_function', None)
    if wrapped is None:
        signature = inspect.getargspec(function)
    else:
        signature = inspect.getargspec(wrapped)
    defaults = signature.defaults
    if method:
        args = signature.args[1:]
    else:
        args = signature.args
    if defaults:
        kwargs = zip(args[-len(defaults):], defaults)
        args = args[:-len(defaults)]
    else:
        kwargs = []
    st = '%s.%s(' % (clean_module_name(function.__module__), function.__name__)

    for a in args:
        st += str(a) + ', '
    for a, v in kwargs:
        if isinstance(v, str):
            v = '\'' + v + '\''
        st += str(a) + '=' + str(v) + ', '
    if kwargs or args:
        signature = st[:-2] + ')'
    else:
        signature = st + ')'
    return post_process_signature(signature)


def get_class_signature(cls):
    try:
        class_signature = get_function_signature(cls.__init__)
        class_signature = class_signature.replace('__init__', cls.__name__)
    except (TypeError, AttributeError):
        # in case the class inherits from object and does not
        # define __init__
        class_signature = "{clean_module_name}.{cls_name}()".format(
            clean_module_name=clean_module_name(cls.__module__),
            cls_name=cls.__name__
        )
    return post_process_signature(class_signature)


def post_process_signature(signature):
    parts = re.split(r'\.(?!\d)', signature)
    if len(parts) >= 4:
        if parts[1] == 'layers':
            signature = 'keras.layers.' + '.'.join(parts[3:])
        if parts[1] == 'utils':
            signature = 'keras.utils.' + '.'.join(parts[3:])
        if parts[1] == 'backend':
            signature = 'keras.backend.' + '.'.join(parts[3:])
    return signature


def clean_module_name(name):
    if name.startswith('keras_applications'):
        name = name.replace('keras_applications', 'keras.applications')
    if name.startswith('keras_preprocessing'):
        name = name.replace('keras_preprocessing', 'keras.preprocessing')
    assert name[:6] == 'pyaer.', 'Invalid module name: %s' % name
    return name


def class_to_docs_link(cls):
    module_name = clean_module_name(cls.__module__)
    module_name = module_name[6:]
    link = ROOT + module_name.replace('.', '/') + '#' + cls.__name__.lower()
    return link


def class_to_source_link(cls):
    module_name = clean_module_name(cls.__module__)
    path = module_name.replace('.', '/')
    path += '.py'
    line = inspect.getsourcelines(cls)[-1]
    link = ('https://github.com/duguyue100/'
            'pyaer/blob/master/' + path + '#L' + str(line))
    return '[[source]](' + link + ')'


def code_snippet(snippet):
    result = '```python\n'
    result += snippet + '\n'
    result += '```\n'
    return result


def count_leading_spaces(s):
    ws = re.search(r'\S', s)
    if ws:
        return ws.start()
    else:
        return 0


def process_list_block(docstring, starting_point, leading_spaces, marker):
    ending_point = docstring.find('\n\n', starting_point)
    block = docstring[starting_point:(None if ending_point == -1 else
                                      ending_point - 1)]
    # Place marker for later reinjection.
    docstring = docstring.replace(block, marker)
    lines = block.split('\n')
    # Remove the computed number of leading white spaces from each line.
    lines = [re.sub('^' + ' ' * leading_spaces, '', line) for line in lines]
    # Usually lines have at least 4 additional leading spaces.
    # These have to be removed, but first the list roots have to be detected.
    top_level_regex = r'^    ([^\s\\\(]+):(.*)'
    top_level_replacement = r'- __\1__:\2'
    lines = [re.sub(top_level_regex, top_level_replacement, line) for line in lines]
    # All the other lines get simply the 4 leading space (if present) removed
    lines = [re.sub(r'^    ', '', line) for line in lines]
    # Fix text lines after lists
    indent = 0
    text_block = False
    for i in range(len(lines)):
        line = lines[i]
        spaces = re.search(r'\S', line)
        if spaces:
            # If it is a list element
            if line[spaces.start()] == '-':
                indent = spaces.start() + 1
                if text_block:
                    text_block = False
                    lines[i] = '\n' + line
            elif spaces.start() < indent:
                text_block = True
                indent = spaces.start()
                lines[i] = '\n' + line
        else:
            text_block = False
            indent = 0
    block = '\n'.join(lines)
    return docstring, block


def process_docstring(docstring):
    # First, extract code blocks and process them.
    code_blocks = []
    if '```' in docstring:
        tmp = docstring[:]
        while '```' in tmp:
            tmp = tmp[tmp.find('```'):]
            index = tmp[3:].find('```') + 6
            snippet = tmp[:index]
            # Place marker in docstring for later reinjection.
            docstring = docstring.replace(
                snippet, '$CODE_BLOCK_%d' % len(code_blocks))
            snippet_lines = snippet.split('\n')
            # Remove leading spaces.
            num_leading_spaces = snippet_lines[-1].find('`')
            snippet_lines = ([snippet_lines[0]] +
                             [line[num_leading_spaces:]
                             for line in snippet_lines[1:]])
            # Most code snippets have 3 or 4 more leading spaces
            # on inner lines, but not all. Remove them.
            inner_lines = snippet_lines[1:-1]
            leading_spaces = None
            for line in inner_lines:
                if not line or line[0] == '\n':
                    continue
                spaces = count_leading_spaces(line)
                if leading_spaces is None:
                    leading_spaces = spaces
                if spaces < leading_spaces:
                    leading_spaces = spaces
            if leading_spaces:
                snippet_lines = ([snippet_lines[0]] +
                                 [line[leading_spaces:]
                                  for line in snippet_lines[1:-1]] +
                                 [snippet_lines[-1]])
            snippet = '\n'.join(snippet_lines)
            code_blocks.append(snippet)
            tmp = tmp[index:]

    # Format docstring lists.
    section_regex = r'\n( +)# (.*)\n'
    section_idx = re.search(section_regex, docstring)
    shift = 0
    sections = {}
    while section_idx and section_idx.group(2):
        anchor = section_idx.group(2)
        leading_spaces = len(section_idx.group(1))
        shift += section_idx.end()
        marker = '$' + anchor.replace(' ', '_') + '$'
        docstring, content = process_list_block(docstring,
                                                shift,
                                                leading_spaces,
                                                marker)
        sections[marker] = content
        section_idx = re.search(section_regex, docstring[shift:])

    # Format docstring section titles.
    docstring = re.sub(r'\n(\s+)# (.*)\n',
                       r'\n\1__\2__\n\n',
                       docstring)

    # Strip all remaining leading spaces.
    lines = docstring.split('\n')
    docstring = '\n'.join([line.lstrip(' ') for line in lines])

    # Reinject list blocks.
    for marker, content in sections.items():
        docstring = docstring.replace(marker, content)

    # Reinject code blocks.
    for i, code_block in enumerate(code_blocks):
        docstring = docstring.replace(
            '$CODE_BLOCK_%d' % i, code_block)
    return docstring

print('Cleaning up existing sources directory.')
if os.path.exists('sources'):
    shutil.rmtree('sources')

print('Populating sources directory with templates.')
for subdir, dirs, fnames in os.walk('pages'):
    for fname in fnames:
        new_subdir = subdir.replace('pages', 'sources')
        if not os.path.exists(new_subdir):
            os.makedirs(new_subdir)
        if fname[-3:] == '.md':
            fpath = os.path.join(subdir, fname)
            new_fpath = fpath.replace('pages', 'sources')
            shutil.copy(fpath, new_fpath)


def read_file(path):
    with open(path) as f:
        return f.read()


def collect_class_methods(cls, methods):
    if isinstance(methods, (list, tuple)):
        return [getattr(cls, m) if isinstance(m, str) else m for m in methods]
    methods = []
    for _, method in inspect.getmembers(cls, predicate=inspect.isroutine):
        if method.__name__[0] == '_' or method.__name__ in EXCLUDE:
            continue
        methods.append(method)
    return methods


def render_function(function, method=True):
    subblocks = []
    signature = get_function_signature(function, method=method)
    if method:
        signature = signature.replace(
            clean_module_name(function.__module__) + '.', '')
    subblocks.append('### ' + function.__name__ + '\n')
    subblocks.append(code_snippet(signature))
    docstring = function.__doc__
    if docstring:
        subblocks.append(process_docstring(docstring))
    return '\n\n'.join(subblocks)


def read_page_data(page_data, type):
    assert type in ['classes', 'functions', 'methods']
    data = page_data.get(type, [])
    for module in page_data.get('all_module_{}'.format(type), []):
        module_data = []
        for name in dir(module):
            if name[0] == '_' or name in EXCLUDE:
                continue
            module_member = getattr(module, name)
            if (inspect.isclass(module_member) and type == 'classes' or
               inspect.isfunction(module_member) and type == 'functions'):
                instance = module_member
                if module.__name__ in instance.__module__:
                    if instance not in module_data:
                        module_data.append(instance)
        module_data.sort(key=lambda x: id(x))
        data += module_data
    return data


if __name__ == '__main__':
    readme = read_file('../README.md')
    index = read_file('pages/index.md')
    index = index.replace('{{autogenerated}}', readme[readme.find('##'):])
    with open('sources/index.md', 'w') as f:
        f.write(index)

    print('Generating docs for PyAER %s.' % pyaer.__about__.__version__)
    for page_data in PAGES:
        classes = read_page_data(page_data, 'classes')

        blocks = []
        for element in classes:
            if not isinstance(element, (list, tuple)):
                element = (element, [])
            cls = element[0]
            subblocks = []
            signature = get_class_signature(cls)
            subblocks.append('<span style="float:right;">' +
                             class_to_source_link(cls) + '</span>')
            if element[1]:
                subblocks.append('## ' + cls.__name__ + ' class\n')
            else:
                subblocks.append('### ' + cls.__name__ + '\n')
            subblocks.append(code_snippet(signature))
            docstring = cls.__doc__
            if docstring:
                subblocks.append(process_docstring(docstring))
            methods = collect_class_methods(cls, element[1])
            if methods:
                subblocks.append('\n---')
                subblocks.append('## ' + cls.__name__ + ' methods\n')
                subblocks.append('\n---\n'.join(
                    [render_function(method, method=True) for method in methods]))
            blocks.append('\n'.join(subblocks))

        methods = read_page_data(page_data, 'methods')

        for method in methods:
            blocks.append(render_function(method, method=True))

        functions = read_page_data(page_data, 'functions')

        for function in functions:
            blocks.append(render_function(function, method=False))

        if not blocks:
            raise RuntimeError('Found no content for page ' +
                               page_data['page'])

        mkdown = '\n----\n\n'.join(blocks)
        # save module page.
        # Either insert content into existing page,
        # or create page otherwise
        page_name = page_data['page']
        path = os.path.join('sources', page_name)
        if os.path.exists(path):
            template = read_file(path)
            assert '{{autogenerated}}' in template, ('Template found for ' + path +
                                                     ' but missing {{autogenerated}}'
                                                     ' tag.')
            mkdown = template.replace('{{autogenerated}}', mkdown)
            print('...inserting autogenerated content into template:', path)
        else:
            print('...creating new page with autogenerated content:', path)
        subdir = os.path.dirname(path)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        with open(path, 'w') as f:
            f.write(mkdown)
