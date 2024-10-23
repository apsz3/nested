; Asserts a == b
(defmacro asseq (a b) (assert (= a b)))

; define 
(defmacro defn (name args body)
    (let name (lambda args body)))
