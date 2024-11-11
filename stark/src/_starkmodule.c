#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* interface_add_node(PyObject* self, PyObject* args){
    (void) self;

    PyObject * children_key = Py_BuildValue("s#", "children", 8);

    PyObject * dict_tree;

    if(!PyArg_ParseTuple(args, "O!", &PyDict_Type, &dict_tree)){
        PyErr_SetString(PyExc_Exception, "Failed to parse arguments!");
        return NULL;
    }

    #ifndef NDEBUG
    if(!PyDict_Check(dict_tree)){
        PyErr_SetString(PyExc_Exception, "Argument of add_node must be a dict.");
        return NULL;
    }
    #endif

    const int res_contains = PyDict_Contains(dict_tree, children_key);

    PyObject * list_children;

    switch(res_contains){
        case -1:
            PyErr_SetString(PyExc_Exception, "Failed to test for 'contain'.");
            return NULL;
        case 0:
            list_children = PyList_New(1);
            PyList_SetItem(list_children, 0, PyDict_New());
            PyDict_SetItem(dict_tree, children_key, list_children);
            break;
        case 1:
            list_children = PyDict_GetItem(dict_tree, children_key);
            PyList_Append(list_children, PyDict_New());
            break;
    }

    return Py_None;
}

static PyMethodDef _starkmethods[] = {
    {"add_node", interface_add_node, METH_VARARGS, "Add a node."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef _starkmodule = {
    PyModuleDef_HEAD_INIT,
    "_stark",
    NULL, // docs
    -1,
    _starkmethods,
	NULL, // PyModuleDef_Slot* m_slots, but NULL if single phase initialisation
	NULL, // traverseproc m_traverse, "A traversal function to call during GC traversal of the module object, or NULL if not needed"
	NULL, // inquiry m_clear, "A clear function to call during GC clearing of the module object, or NULL if not needed"
	NULL, // freefunc m_free, "A function to call during deallocation of the module object, or NULL if not needed"
};

PyMODINIT_FUNC PyInit__stark(void){
    PyObject* mod = PyModule_Create(&_starkmodule);
    return mod;
}
