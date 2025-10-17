`get_num_types` function is not used by `effective_damage`

Ensure `get_num_types` is called by
`effective_damage` to determine the attacker's
number of types. Check if you inadvertently
re-implemented its logic instead of calling the
function. Consider revisiting function calls and
modularity concepts.