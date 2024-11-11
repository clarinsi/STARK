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

Py_ssize_t get_query_tree_size(PyObject* query_tree){
    Py_ssize_t size = 1;

    PyObject * list_children;

    PyObject * children_key = Py_BuildValue("s#", "children", 8);


    const int res_contains = PyDict_Contains(query_tree, children_key);

    Py_ssize_t i;

    switch(res_contains){
        /*
        case -1:
            PyErr_SetString(PyExc_Exception, "Failed to test for 'contain'.");
            return NULL;
        */
        case 0:
            break;
        case 1:
            list_children = PyDict_GetItem(query_tree, children_key);

            Py_ssize_t len_list_children = PyList_Size(list_children);

            for(i = 0 ; i < len_list_children ; i++){
                size += get_query_tree_size(PyList_GetItem(list_children, i));
            }

            break;
    }

    return size;
}

static PyObject* interface_get_query_tree_size_range(PyObject* self, PyObject*
args){
    (void) self;

    Py_ssize_t min_size = 1000000;
    Py_ssize_t max_size = 0;

    PyObject * list_query_trees;

    if(!PyArg_ParseTuple(args, "O!", &PyList_Type, &list_query_trees)){
        PyErr_SetString(PyExc_Exception, "Failed to parse arguments!");
        return NULL;
    }

    const Py_ssize_t len_list_query_trees = PyList_Size(list_query_trees);
    Py_ssize_t i;
    for(i = 0 ; i < len_list_query_trees ; i++){
        Py_ssize_t size = get_query_tree_size(PyList_GetItem(list_query_trees,
        i));
        if(size > max_size){max_size = size;}
        if(size < min_size){min_size = size;}
    }

    PyObject * return_tuple = PyTuple_New(2);
    PyTuple_SetItem(return_tuple, 0, Py_BuildValue("i", min_size));
    PyTuple_SetItem(return_tuple, 1, Py_BuildValue("i", max_size));

    return return_tuple;
}



static PyObject* interface_create_ngrams_query_trees(PyObject* self, PyObject*
args){
    (void) self;

    int32_t n;
    PyObject * list_trees;
    PyObject * list_new_trees;

    if(!PyArg_ParseTuple(args, "iO!", &n, &PyList_Type, &list_trees)){
        PyErr_SetString(PyExc_Exception, "Failed to parse arguments!");
        return NULL;
    }

    PyObject * globals = PyEval_GetGlobals();
    PyObject * key_tree_grow = PyUnicode_FromString("tree_grow");
    PyObject * tree_grow_func = PyDict_GetItem(globals, key_tree_grow);

    // PyObject * tree_grow_args = PyTuple_New(1);

    Py_ssize_t card_trees = PyList_Size(list_trees);
    Py_ssize_t card_new_trees = 0;

    Py_ssize_t capacity_trees = card_trees;
    Py_ssize_t capacity_new_trees = capacity_new_trees;

    list_new_trees = PyList_New(card_new_trees);

    int32_t i;
    for(i = 0 ; i < n ; i++){

        // card_trees = PyList_Size(list_trees);
        Py_ssize_t j;
        for(j = 0 ; j < card_trees ; j++){
            PyObject * tree = PyList_GetItem(list_trees, j);
    
            /*
            PyTuple_SetItem(tree_grow_args, 0, tree);
            PyObject * tree_grow_iterator = PyObject_CallObject(tree_grow_func,
            tree_grow_args);
            */
            PyObject * tree_grow_iterator = \
            PyObject_CallOneArg(tree_grow_func, tree);

            PyObject * new_tree;

            while((new_tree = PyIter_Next(tree_grow_iterator))){
                int32_t duplicate = 0;

                // card_new_trees = PyList_Size(new_tree);
                Py_ssize_t k;
                for(k = 0 ; k < card_new_trees ; k++){
                    PyObject * confirmed_new_tree = \
                    PyList_GetItem(list_new_trees, k);

                    if(PyObject_RichCompareBool(new_tree, confirmed_new_tree,
                    Py_EQ)){
                        duplicate = 1;
                        break;
                    }
                }

                if(!duplicate){
                    if(card_new_trees == capacity_new_trees){
                        PyList_Append(list_new_trees, new_tree);
                        capacity_new_trees++;
                    } else {
                        PyList_SetItem(list_new_trees, card_new_trees,
                        new_tree);
                    }
                    card_new_trees++;
                }
            }

        }

        void* mem = list_trees;
        // Py_ssize_t mem_card = card_trees;
        Py_ssize_t mem_capacity = capacity_trees;

        list_trees = list_new_trees;
        card_trees = card_new_trees;
        capacity_trees = capacity_new_trees;

        list_new_trees = mem;
        // card_new_trees = mem_card;
        card_new_trees = 0;
        capacity_new_trees = mem_capacity;

        // Py_DECREF(list_trees);
        PyGC_Collect();
    }

    // return list_trees;
    return PyList_GetSlice(list_trees, 0, card_trees);
}

static PyMethodDef _starkmethods[] = {
    {"add_node", interface_add_node, METH_VARARGS, "Add a node."},
    {"get_query_tree_size_range", interface_get_query_tree_size_range,
    METH_VARARGS, "Returns a tuple of (min_size, max_size)."},
    {"create_ngrams_query_trees", interface_create_ngrams_query_trees,
    METH_VARARGS, "Forms unique ngram query trees."},
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
