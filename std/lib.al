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
(defmacro test-all (ls) (begin
    (let loop (lambda (NOT-LS) (
        (if (not (empty? NOT-LS))
            (begin
                (print (hd NOT-LS))
                (loop (rst NOT-LS)))
            (print "done")))))
    (loop ls)))


(test-all '(1 2 3 2 2 2 2 2 2 2 2 2))