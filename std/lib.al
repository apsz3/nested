; define 
(defmacro defn (name args body)
    (let name (lambda args body)))

; Asserts a == b
(defmacro asseq (a b) (assert (= a b)))
; Asserts fn(a) == b
; eventually: (if (param-set 'debug) ...)
(defmacro test (fn input expected) (asseq (fn input) expected))

(defmacro empty? (ls) (= ls 'empty))

;; (let len (lambda (ls)
;;     (if (empty? ls)
;;         0
;;         (+ 1 (len (rst ls))))))
;; (test len 'empty 0)


; NOTE: IF YOU STICK A PARAMATER NAME IN THE INNER FUNCTION
; THAT MATCHES THE NAME OF AN ARGUMENT TO THE MACRO
; THINGS WILL NOT WORK AS EXPECTED!!!!
; TODO: FIX THIS IN MACRO CODE SO THAT WE SCOPE PROPERLY
(defmacro test-all (ls) (begin
    (let loop (lambda (not-ls) (
        (if (not (empty? not-ls))
            (begin
                (let inner (hd not-ls))
                (let fn (hd inner))
                (print fn)
                (let input (hd (rst inner)))
                (let expected (hd (rst (rst inner))))
                ; TODO: REVERSE ORDER OF PRINT!!!
                (print "Testing function" fn 
                    "on intput" input
                    "expecting" expected)
                (test fn input expected)
                (loop (rst not-ls)))
            (print "done")))))
    (loop ls)))

; Curesd but works; if we use # in identifiers names internally for macros,
; and disallow it in the grammar, then we can guarantee a user never
; mistakenly calls a macro alias....
;(loop#0 (list 1 2 3))

; TODO: can we make it so outer scope just doesn't have the macro aliases?
; No, because macros always go into the global scope, they're not functions!?
(let id (lambda (x) x))
(test-all (list 
    (list id 1 1) ; Do we need quasiquote here? How does 1 get coerced to int?
    (list id 2 2)))
;; ))
;; (test id 1 1)
;; (test-all '(
;;         (empty? '() 't)
;;         (empty? '() 't )))