const today = new Date()
const syncState = document.querySelector('.csyncstate')
var selectedDay = null

const eventSource = new EventSource('http://localhost:717/getdata');
var events = []

eventSource.onopen = () => {
    console.log("SSE 连接已成功建立。");
};

eventSource.onmessage = (str) => {
    console.log("收到数据");
    data = decodeEvents(str.data)
    online = data.state
    events = data.events;
    applyAllPlan(events, document.querySelector('.cflow'));
    applyAllMarker(events, document.querySelector('.cgrid'));

    console.log(online)
    syncState.textContent = online ? "" : "未同步"
}

eventSource.onerror = (event) => {
    // var state = 
    if (eventSource.readyState === EventSource.CONNECTING) {
        syncState.textContent = "未连接"
        console.log("网络中断，正在尝试重连...");
    } else {
        syncState.textContent = "出错"
        console.log("未知错误状态");
    }
};


initCalender()

function decodeEvents(jsonString) {
    var events;
    try {
        events = JSON.parse(jsonString);
    } catch (error) {
        console.error("解析 JSON 失败:", error);
        events = []
    }
    return events
}


function initCalender() {
    // 填充标题
    const cmonth = document.querySelector('.cmonth')
    cmonth.textContent = `${today.getFullYear()} 年 ${today.getMonth() + 1} 月 ${today.getDate()} 日`
    cmonth.onclick = () => { applyAllPlan(events, document.querySelector('.cflow')) };
    
    // 填充日历主体
    const cgrid = document.querySelector('.cgrid')

    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);

    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    const endDate = new Date(lastDay);
    endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()));

    const totalDays = dateSub(startDate, endDate) + 1;
    if (totalDays < 36) {
        endDate.setDate(endDate.getDate() + 7);
    }

    for (let day = new Date(startDate); day <= endDate; day.setDate(day.getDate() + 1)) {
        const dateItem = document.createElement('div')
        dateItem.className = 'cday';
        dateItem.textContent = `${day.getDate()}`;

        const isToday = day.getFullYear() === today.getFullYear() && day.getMonth() === today.getMonth() && day.getDate() === today.getDate();
        
        if (isToday) {
            dateItem.classList.add('today');
        }

        if (day < firstDay || day > lastDay) {
            dateItem.classList.add('cother-month')
        }

        let _day = new Date(day);
        dateItem.onclick = () => { onDaySelected(_day) };
        cgrid.appendChild(dateItem);
    }
}


function applyAllPlan(events, flow) {
    if (events.length === 0) {
        flow.textContent = "无日程";
        return;
    }

    flow.innerHTML = '';

    events.forEach(event => {
        const startDate = new Date(event.start);
        const endDate = new Date(event.end);
        
        const itemDiv = document.createElement('div');
        itemDiv.className = 'citem';
        
        if (!isInFuture(endDate, today));
        else
            if (event.note.includes('倒计时')) {
            const titleP = document.createElement('p');
            titleP.className = 'countdown';
            titleP.textContent = `${event.title}还有 ${dateSub(today, startDate)} 天`;

            itemDiv.appendChild(titleP)
            flow.prepend(itemDiv)
        } else {
            const titleP = document.createElement('p');
            titleP.className = 'title';
            titleP.textContent = event.title;

            const dateP = document.createElement('p');
            dateP.className = 'date';
            dateP.textContent = formatDateRange(startDate, endDate);

            itemDiv.appendChild(titleP);
            itemDiv.appendChild(dateP);

            flow.appendChild(itemDiv);
        }
    });
}


function applyAllMarker(events, grid) {
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const cStartDate = new Date(firstDay);
    cStartDate.setDate(cStartDate.getDate() - firstDay.getDay());

    const scheduledIndices = new Set();

    events.forEach(event => {
        const startDate = new Date(event.start);
        const endDate = new Date(event.end);

        let _day = new Date(startDate);
        _day.setHours(0, 0, 0 ,0);
        for (; _day <= endDate; _day.setDate(_day.getDate() + 1)) {
            let dayNum = dateSub(cStartDate, _day)
            if (dayNum < 0)
                continue;
            scheduledIndices.add(dayNum)
        }
    })

    const dayBoxs = grid.children;

    for (let dayNum of scheduledIndices) {
        if (dayNum < dayBoxs.length) {
            let ori = dayBoxs[dayNum].querySelector('div.mark')
            if (ori) ori.remove();
            dayBoxs[dayNum].appendChild(makeSimpleMark())
        }
    }
}


function applyOneDayPlan(events, date, flow) {
    flow.replaceChildren()
    let eventList = [];
    let dateSmallLimit = new Date(date)    
    dateSmallLimit.setHours(0, 0, 0, 0);
    let dateBigLimit = new Date(dateSmallLimit);
    dateBigLimit.setDate(dateSmallLimit.getDate() + 1);

    
    let headItem = document.createElement('div');
    headItem.className = 'citem';
    let head = document.createElement('p');
    head.className = 'countdown';
    headItem.appendChild(head);
    head.textContent = `${date.getMonth() + 1} 月 ${date.getDate()} 日的日程`;
    flow.appendChild(headItem)


    events.forEach(event => {
        const startDate = new Date(event.start);
        const endDate = new Date(event.end);

        if (
            !(endDate < dateSmallLimit && startDate < dateSmallLimit) &&
            !(endDate > dateBigLimit && startDate > dateBigLimit)
        ) {
            let item = {};
            item.start = (event.start < dateSmallLimit) ? new Date(dateSmallLimit) : new Date(event.start);
            item.end = (event.end > dateBigLimit) ? new Date(dateBigLimit) : new Date(event.end);
            item.title = event.title;
            eventList.push(item)
        }
    })

    eventList.sort((a, b) => a.start - b.start);

    eventList.forEach(event => {
        const itemDiv = document.createElement('div')
        itemDiv.className = 'citem';

        const titleP = document.createElement('p');
        titleP.className = 'time';
        titleP.textContent = `${event.start.getHours().toString().padStart(2, '0')}:${event.start.getMinutes().toString().padStart(2, '0')} - ${event.end.getHours().toString().padStart(2, '0')}:${event.end.getMinutes().toString().padStart(2, '0')}`;

        const dateP = document.createElement('p');
        dateP.className = 'plan';
        dateP.textContent = event.title;

        itemDiv.appendChild(titleP);
        itemDiv.appendChild(dateP);

        flow.appendChild(itemDiv);
    })

    if (eventList.length === 0) {
        let noplan = document.createElement('div');
        noplan.className = 'citem';
        noplan.textContent = '今日无安排';
        flow.appendChild(noplan);
    }
}


function formatDateRange(startDate, endDate) {
    const formatTime = (date) => {
        const hours = date.getHours();
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    };

    const formatDate = (date) => {
        return `${date.getMonth() + 1}月${date.getDate()}日`;
    };

    const startFormattedDate = formatDate(startDate);
    const startFormattedTime = formatTime(startDate);

    const endFormattedDate = formatDate(endDate);
    const endFormattedTime = formatTime(endDate);

    const isSameDay = startDate.getFullYear() === endDate.getFullYear() &&
                      startDate.getMonth() === endDate.getMonth() &&
                      startDate.getDate() === endDate.getDate();

    if (isSameDay) {
        return `${startFormattedDate} ${startFormattedTime} - ${endFormattedTime}`;
    } else {
        return `${startFormattedDate} ${startFormattedTime} - ${endFormattedDate} ${endFormattedTime}`;
    }
}


function dateSub(day, futureDay) {
    const MS_PER_DAY = 1000 * 60 * 60 * 24;

    const utcA = Date.UTC(day.getFullYear(), day.getMonth(), day.getDate());
    const utcB = Date.UTC(futureDay.getFullYear(), futureDay.getMonth(), futureDay.getDate());

    return Math.floor((utcB - utcA) / MS_PER_DAY);
}


function isInFuture(time, today = new Date()) {
    // const today = new Date();
    return time > today;
}


function makeSimpleMark() {
    mark = document.createElement('div')
    mark.classList.add('easy');
    mark.classList.add('mark');
    return mark;
}


function setDateZero(date) {
    date.setHours(0);
    date.setMinutes(0);
    date.setSeconds(0);

    return date;
}


function onDaySelected(date) {
    selectedDay = new Date(date)
    applyOneDayPlan(events, date, document.querySelector('.cflow'))
}


function getColorFromWE(color) {
    var customColor = color.split(' ');
    customColor = customColor.map(function(c) {
        return Math.ceil(c * 255);
    });
    return 'rgb(' + customColor + ')';
}


// For Wallpaper Engine
window.wallpaperPropertyListener = {
    applyUserProperties: function (properties) {
        const root = document.documentElement;
        if (properties.fontsize) {
            root.style.setProperty('--html-fontsize', `${properties.fontsize.value}px`)
        }
        if (properties.vermargin) {
            root.style.setProperty('--ver-margin', `${properties.vermargin.value}rem`)
        }
        if (properties.hormargin) {
            root.style.setProperty('--hor-margin', `${properties.hormargin.value}rem`)
        }
        if (properties.primarycolor) {
            var color = getColorFromWE(properties.primarycolor.value)
            root.style.setProperty('--primary-color', color)
        }
        if (properties.background) {
            if (properties.background.value) { 
                root.style.setProperty('--background-file', "url('file:///" + properties.background.value + "')");
            } else {
                root.style.setProperty('--background-file', "url('background.jpg')")
            }  
        }
        if (properties.forward) {
            switch (properties.forward.value) {
                case "right":
                    root.style.setProperty('--forward', 'flex-end'); break;
                case "left":
                    root.style.setProperty('--forward', 'flex-start'); break;
                case "center":
                    root.style.setProperty('--forward', 'center'); break;
            }
        }
    },
};