; define 
(defmacro defn (name args body)
    (let name (lambda args body)))

; Asserts a == b
(defmacro asseq (a b) (assert (= a b)))
(defmacro test (fn input expected) (asseq (fn input) expected))

(defmacro empty? (ls) (= ls 'empty))

(let len (lambda (ls)
    (if (empty? ls)
        0
        (+ 1 (len (rst ls))))))

(test len (list 2 3 5) 3)
