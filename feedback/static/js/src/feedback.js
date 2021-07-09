/* Javascript for FeedbackXBlock. */
function FeedbackXBlock(runtime, element) {

    // TODO: Get course id a better way, the requests below do not work

    // const httpPost = (url) => {
    //     var xmlHttp = new XMLHttpRequest();
    //     xmlHttp.open("POST", url, false);
    //     xmlHttp.send(null);
    //     return xmlHttp.responseText;
    // }

    // $.post(courseId, "").done(function(res) {
    //     console.log("COURSE ID: " + res)
    // })

    // var courseId = runtime.handlerUrl(element, 'get_course_id');

    const get_course_id = (url) => {
        if (url.indexOf('courses.') > -1) {
            return $('[data-course-id]').toArray()[0].getAttribute('data-course-id')
        } else if (url.indexOf('studio.') > -1) {
            return $('[data-course-key]').toArray()[0].getAttribute('data-course-key')
        } else {
            return ""
        }
    }

    const get_form_url = () => {
        const protocol = document.location.protocol
        const host = clean_host(document.location.host);
        const course_id = get_course_id(document.location.host);
        return protocol + "//" + host + "/courses/" + course_id + "/feedback/new?embed=true";
    };

    const clean_host = (url) => {
        return url.replace(/(courses.)|(studio.)/, "");
    };
    
    $(function () {
        /* Here's where you'd do things on page load. */
        const frame = document.createElement('iframe');
        frame.title="Feedback Form";
        frame.src=get_form_url();
        frame.height='700rem';
        frame.width='100%';
        $('.feedback_block').toArray()[0].appendChild(frame);
    });
}
