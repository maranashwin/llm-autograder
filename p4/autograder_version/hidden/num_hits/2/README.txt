function output is incorrect when the `attacker` cannot do any damage to the `defender`

Ensure `num_hits` correctly handles cases where the
`attacker` can do zero effective damage to `defender`.
In this case, `num_hits` should return 'infinitely many'. 
Review handling of division by zero and conditions 
for effective damage.