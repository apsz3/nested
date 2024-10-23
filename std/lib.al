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



(defmacro test-all (ls) (begin
    (let loop (lambda (ls) (
        (if (not (empty? ls))
            (begin
                (print (hd ls))
                (loop (rst ls)))
            (print "done")))))
    (loop ls)))


(test-all '(1 2 3))