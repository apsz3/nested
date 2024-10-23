
; Maybe just define no args () for a macro with no args ... seems to
; work, lol
(defmacro test-hygenic (begin
    (let x 2)
))

(let res (lambda () 
    (begin 
        (let x 0)
        (test-hygenic)
        x)))

(print (res))
